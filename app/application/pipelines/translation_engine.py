from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Optional

from app.application.pipelines.pipeline_executor import (
    PipelineExecutionRequest,
    PipelineExecutionResult,
    PipelineExecutor,
)

log = logging.getLogger(__name__)


@dataclass(slots=True)
class EngineCallbacks:
    """Optional hooks emitted around executor runs."""

    on_run_started: Optional[Callable[[str, PipelineExecutionRequest], None]] = None
    on_run_finished: Optional[Callable[[str, PipelineExecutionResult], None]] = None


@dataclass(slots=True)
class ExecutorEntry:
    executor: PipelineExecutor
    graph_path: Path
    executor_params: dict
    lock: threading.Lock = field(default_factory=threading.Lock)
    prepared: bool = False
    invalidated: bool = False


class TranslationEngine:
    """Coordinates pipeline executors with simple caching and FIFO scheduling."""

    def __init__(
        self,
        make_executor: Callable[[Path], PipelineExecutor],
        *,
        callbacks: Optional[EngineCallbacks] = None,
        cpu_worker_cap: int = 4,
        cpu_worker_fraction: float = 1.0,
    ) -> None:
        self._make_executor = make_executor
        self._callbacks = callbacks or EngineCallbacks()
        self._entries: Dict[str, ExecutorEntry] = {}
        self._entries_lock = threading.Lock()
        cpu_count = os.cpu_count() or 1
        cpu_workers = max(1, min(cpu_worker_cap, int(cpu_count * cpu_worker_fraction)))
        self._cpu_slots = threading.Semaphore(cpu_workers)
        self._gpu_slots = threading.Semaphore(1)

    def ensure_executor(
        self,
        pipeline_id: str,
        graph_path: Path,
        executor_params: Optional[dict] = None,
    ) -> ExecutorEntry:
        """Fetch or build a prepared executor entry for the given pipeline."""
        cleanup_executor = None
        with self._entries_lock:
            entry = self._entries.get(pipeline_id)
            needs_reset = entry is None or entry.graph_path != graph_path or (entry and entry.invalidated)
            if needs_reset:
                cleanup_executor = entry.executor if entry else None
                entry = ExecutorEntry(
                    executor=self._make_executor(graph_path),
                    graph_path=graph_path,
                    executor_params=executor_params or {},
                )
                self._entries[pipeline_id] = entry
            elif entry.executor_params != (executor_params or {}):
                entry.executor_params = executor_params or {}
                entry.prepared = False

        if cleanup_executor:
            self._safe_cleanup(cleanup_executor)

        with entry.lock:
            if entry.invalidated:
                self._safe_cleanup(entry.executor)
                entry.executor = self._make_executor(graph_path)
                entry.graph_path = graph_path
                entry.prepared = False
                entry.invalidated = False
            if not entry.prepared:
                entry.executor.prepare(graph_path, executor_params=entry.executor_params)
                entry.prepared = True
        return entry

    def invalidate(self, pipeline_id: str) -> None:
        """Mark a cached executor stale so it reloads on next use."""
        with self._entries_lock:
            entry = self._entries.get(pipeline_id)
            if entry:
                entry.invalidated = True
                entry.prepared = False

    def run(self, pipeline_id: str, graph_path: Path, request: PipelineExecutionRequest) -> PipelineExecutionResult:
        slot = self._acquire_slot(request)
        try:
            entry = self.ensure_executor(pipeline_id, graph_path, request.executor_params)
            with entry.lock:
                self._fire_started(pipeline_id, request)
                run_started = time.perf_counter()
                result = entry.executor.run(request)
                run_duration_ms = (time.perf_counter() - run_started) * 1000
            self._log_run_finished(pipeline_id, result, run_duration_ms)
            self._fire_finished(pipeline_id, result)
            return result
        finally:
            slot.release()

    def cleanup(self) -> None:
        """Cleanup all cached executors."""
        with self._entries_lock:
            entries = list(self._entries.values())
            self._entries.clear()
        for entry in entries:
            self._safe_cleanup(entry.executor)

    def _acquire_slot(self, request: PipelineExecutionRequest) -> threading.Semaphore:
        if self._is_gpu_request(request):
            sem = self._gpu_slots
        else:
            sem = self._cpu_slots
        sem.acquire()
        return sem

    @staticmethod
    def _is_gpu_request(request: PipelineExecutionRequest) -> bool:
        device = request.engine_params.device if request.engine_params else None
        if device is None:
            return False
        return str(device).lower() not in ("cpu", "")

    def _fire_started(self, pipeline_id: str, request: PipelineExecutionRequest) -> None:
        if self._callbacks.on_run_started:
            try:
                self._callbacks.on_run_started(pipeline_id, request)
            except Exception:
                pass

    def _fire_finished(self, pipeline_id: str, result: PipelineExecutionResult) -> None:
        if self._callbacks.on_run_finished:
            try:
                self._callbacks.on_run_finished(pipeline_id, result)
            except Exception:
                pass

    @staticmethod
    def _log_run_finished(
        pipeline_id: str,
        result: PipelineExecutionResult,
        run_duration_ms: float,
    ) -> None:
        duration_ms = result.diagnostics.duration_ms if result.diagnostics else run_duration_ms
        if result.error:
            log.warning(
                "Pipeline '%s' finished with error in %.1f ms (%s)",
                pipeline_id,
                duration_ms,
                result.error.code,
            )
            return
        log.info("Pipeline '%s' finished in %.1f ms", pipeline_id, duration_ms)

    @staticmethod
    def _safe_cleanup(executor: PipelineExecutor) -> None:
        try:
            executor.cleanup()
        except Exception:
            pass
