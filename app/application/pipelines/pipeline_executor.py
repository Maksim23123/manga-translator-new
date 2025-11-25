from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

log = logging.getLogger(__name__)


@dataclass(slots=True)
class EngineParams:
    """Hints for engine-level choices (device, mode, priority, timeouts)."""

    device: Optional[str] = None
    mode: Optional[str] = None
    priority: Optional[str] = None
    timeout_s: Optional[float] = None


@dataclass(slots=True)
class PipelineExecutionInput:
    """Standardized pipeline input envelope."""

    images: list[Path] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineExecutionContext:
    """Execution context (e.g., project/session identifiers)."""

    project_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass(slots=True)
class PipelineExecutionRequest:
    """Caller request describing what to run."""

    id: str
    input: PipelineExecutionInput
    executor_params: dict[str, Any] = field(default_factory=dict)
    engine_params: Optional[EngineParams] = None
    context: Optional[PipelineExecutionContext] = None


@dataclass(slots=True)
class PipelineExecutionDiagnostics:
    """Timing/device info collected during a run."""

    duration_ms: float
    graph_path: Optional[Path] = None
    device: Optional[str] = None
    info: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PipelineExecutionError:
    """Structured error surfaced to callers."""

    code: str
    message: str
    detail: Optional[str] = None


@dataclass(slots=True)
class PipelineExecutionResult:
    """Run output plus diagnostics or structured error."""

    id: str
    output: dict[str, Any] = field(default_factory=dict)
    diagnostics: Optional[PipelineExecutionDiagnostics] = None
    error: Optional[PipelineExecutionError] = None


class GraphRunner(Protocol):
    """Abstract runner that knows how to load and execute a pipeline graph."""

    def load(self, graph_path: Path) -> None: ...

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]: ...

    def cleanup(self) -> None: ...


class PipelineExecutor(Protocol):
    """Common executor lifecycle."""

    def prepare(self, graph_path: Path, *, executor_params: Optional[dict[str, Any]] = None) -> None: ...

    def run(self, request: PipelineExecutionRequest) -> PipelineExecutionResult: ...

    def cleanup(self) -> None: ...


class PyFlowPipelineExecutor(PipelineExecutor):
    """Thin wrapper around a graph runner; reusable and engine-agnostic."""

    def __init__(self, runner: GraphRunner, *, graph_path: Optional[Path] = None) -> None:
        self._runner = runner
        self._graph_path = graph_path
        self._prepared_path: Optional[Path] = None
        self._executor_params: dict[str, Any] = {}

    @property
    def graph_path(self) -> Optional[Path]:
        return self._prepared_path or self._graph_path

    def prepare(self, graph_path: Optional[Path] = None, *, executor_params: Optional[dict[str, Any]] = None) -> None:
        path = graph_path or self._graph_path
        if not path:
            raise ValueError("graph_path is required to prepare the executor")
        if not path.exists():
            raise FileNotFoundError(path)

        self._runner.load(path)
        self._prepared_path = path
        self._executor_params = executor_params or {}

    def run(self, request: PipelineExecutionRequest) -> PipelineExecutionResult:
        if not self._prepared_path:
            return PipelineExecutionResult(
                id=request.id,
                error=PipelineExecutionError(
                    code="not_prepared",
                    message="Executor has not been prepared; call prepare(graph_path) first",
                ),
            )

        start = time.perf_counter()
        diagnostics: Optional[PipelineExecutionDiagnostics] = None
        try:
            inputs = {
                "images": request.input.images,
                "metadata": request.input.metadata,
                "executor_params": {**self._executor_params, **request.executor_params},
                "engine_params": request.engine_params,
                "context": request.context,
            }
            output = self._runner.run(inputs)
            diagnostics = PipelineExecutionDiagnostics(
                duration_ms=(time.perf_counter() - start) * 1000,
                graph_path=self._prepared_path,
                device=request.engine_params.device if request.engine_params else None,
            )
            return PipelineExecutionResult(id=request.id, output=output, diagnostics=diagnostics)
        except Exception as ex:
            diagnostics = diagnostics or PipelineExecutionDiagnostics(
                duration_ms=(time.perf_counter() - start) * 1000,
                graph_path=self._prepared_path,
            )
            log.exception("Pipeline execution failed for request %s", request.id)
            return PipelineExecutionResult(
                id=request.id,
                diagnostics=diagnostics,
                error=PipelineExecutionError(code="execution_failed", message=str(ex), detail=repr(ex)),
            )

    def cleanup(self) -> None:
        try:
            self._runner.cleanup()
        finally:
            self._prepared_path = None
            self._executor_params = {}
