from __future__ import annotations

from pathlib import Path
import logging
import uuid
from typing import Any, Optional

from app.application.pipelines.events import (
    ActivePipelineChanged,
    PipelineAdded,
    PipelineEventBus,
    PipelineGraphDirtyChanged,
    PipelineGraphLoadWarning,
    PipelineGraphPointerUpdated,
    PipelineListUpdated,
    PreviewImageChanged,
    PipelineRemoved,
    PipelineRenamed,
)
from app.application.pipelines.translation_engine import TranslationEngine
from app.application.pipelines.ports import (
    ActivePipelineStore,
    GraphStoragePort,
    PipelineMetadataRepository,
    PipelinePreviewPort,
    PipelinePreviewStore,
    PyFlowGateway,
)
from app.application.pipelines.pipeline_executor import (
    EngineParams,
    PipelineExecutionContext,
    PipelineExecutionInput,
    PipelineExecutionRequest,
    PipelineExecutionResult,
)
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.domain.pipelines.pipeline_collection import PipelineCollection
from app.domain.pipelines.pipeline_unit import PipelineUnit

log = logging.getLogger(__name__)


class PipelineService:
    """Application service coordinating pipeline operations and PyFlow orchestration."""

    def __init__(
        self,
        *,
        metadata_repo: PipelineMetadataRepository,
        storage: GraphStoragePort,
        pyflow_gateway: PyFlowGateway,
        preview_port: Optional[PipelinePreviewPort] = None,
        preview_store: Optional[PipelinePreviewStore] = None,
        event_bus: Optional[PipelineEventBus] = None,
        active_store: Optional[ActivePipelineStore] = None,
        engine: Optional[TranslationEngine] = None,
    ) -> None:
        self._metadata_repo = metadata_repo
        self._storage = storage
        self._pyflow = pyflow_gateway
        self._preview_port = preview_port
        self._preview_store = preview_store
        self._events = event_bus or PipelineEventBus()
        self._collection = PipelineCollection()
        self._active_store = active_store
        self._engine = engine

        self._pyflow.on_dirty_changed(self._on_dirty_changed)

    @property
    def collection(self) -> PipelineCollection:
        return self._collection

    def configure_storage(
        self,
        project_root: Optional[Path],
        project_id: Optional[str] = None,
        project_meta_path: Optional[Path] = None,
    ) -> None:
        """Point storage at the project root or reset to fallback."""
        self._storage.set_project_context(project_root, project_id=project_id, project_meta_path=project_meta_path)
        self._storage.cleanup_shared_temp()

    def load(self) -> PipelineCollection:
        if self._active_store:
            self._active_store.clear()
        if self._preview_store:
            self._preview_store.clear()

        previous_active = self._collection.active
        self._collection = self._metadata_repo.load()

        # Reset to no active pipeline on load; selection is transient.
        self._collection.set_active(None)
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))

        active = self._collection.active
        if active:
            self._load_graph_or_blank(active)
            self._publish(ActivePipelineChanged(active.name))
            self._hydrate_preview(active)
        else:
            # Attempt to load the previously active pipeline to surface warnings if the graph is missing/corrupt,
            # but do not keep it active after load.
            if previous_active:
                self._load_graph_or_blank(previous_active)
            else:
                self._pyflow.new_blank()
            self._publish(ActivePipelineChanged(None))
            self._emit_preview_changed(None)

        self._cleanup_orphans()
        return self._collection

    def create(self, name: str) -> PipelineUnit:
        draft_pointer = GraphPointer(final_path=None, status=GraphPointerStatus.MISSING)
        previous_active = self._collection.active
        pipeline = self._collection.add_with_name(name, draft_pointer)
        self._metadata_repo.save(self._collection)
        self._publish(PipelineAdded(pipeline.name))
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))

        active = self._collection.active
        if previous_active is not active:
            self._publish(ActivePipelineChanged(active.name if active else None))
            if active and active.graph.active_path():
                self._pyflow.load_graph(active.graph.active_path())  # type: ignore[arg-type]
            else:
                self._pyflow.new_blank()
            if self._active_store:
                self._active_store.set_active(active.name if active else None)
            if active:
                self._hydrate_preview(active)
            else:
                self._emit_preview_changed(None)

        return pipeline

    def rename(self, old_name: str, new_name: str) -> PipelineUnit:
        pipeline = self._collection.rename(old_name, new_name)
        self._metadata_repo.save(self._collection)
        self._publish(PipelineRenamed(old_name=old_name, new_name=new_name))
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))
        if self._preview_store:
            carried_preview = self._preview_store.get_preview(old_name)
            self._preview_store.clear(old_name)
            if carried_preview is None:
                carried_preview = pipeline.preview_path
            if carried_preview is not None:
                self._preview_store.set_preview(pipeline.name, carried_preview)
        if pipeline.preview_path:
            pipeline.set_preview(pipeline.preview_path)
        if self._collection.active is pipeline:
            self._emit_preview_changed(pipeline)
        if self._active_store and self._active_store.get_active() == old_name:
            self._active_store.set_active(pipeline.name)
        return pipeline

    def remove(self, name: str) -> PipelineUnit:
        removed = self._collection.remove(name)
        self._metadata_repo.save(self._collection)
        self._publish(PipelineRemoved(name))
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))

        # Keep final graphs; clean up drafts immediately since they won't be reused.
        if removed.graph.draft_path:
            try:
                removed.graph.draft_path.unlink(missing_ok=True)
            except Exception:
                log.debug("Failed to delete draft graph %s", removed.graph.draft_path, exc_info=True)
        if self._preview_port:
            self._preview_port.delete_preview(removed)
        if self._preview_store:
            self._preview_store.clear(name)

        active = self._collection.active
        self._publish(ActivePipelineChanged(active.name if active else None))
        if self._active_store:
            self._active_store.set_active(active.name if active else None)
        if active and active.graph.active_path():
            self._pyflow.load_graph(active.graph.active_path())  # type: ignore[arg-type]
        else:
            self._pyflow.new_blank()
        if active:
            self._hydrate_preview(active)
        else:
            self._emit_preview_changed(None)

        return removed

    def set_active(self, name: Optional[str]) -> Optional[PipelineUnit]:
        previous_active = self._collection.active
        if previous_active and previous_active.name != name and previous_active.is_dirty:
            self.save_active()

        active = self._collection.set_active(name)
        self._metadata_repo.save(self._collection)
        self._publish(ActivePipelineChanged(active.name if active else None))
        if self._active_store:
            self._active_store.set_active(active.name if active else None)

        if active:
            self._load_graph_or_blank(active)
            self._hydrate_preview(active)
        else:
            self._pyflow.new_blank()
            self._emit_preview_changed(None)

        return active

    def save_active(self) -> Optional[PipelineUnit]:
        active = self._collection.active
        if not active:
            return None

        target_path = self._storage.draft_path_for(active.name)
        log.debug("Saving active pipeline '%s' to draft %s", active.name, target_path)
        self._pyflow.save_graph(target_path)

        draft_pointer = active.graph.mark_draft(target_path)
        active.update_graph(draft_pointer)
        active.clear_dirty()

        self._metadata_repo.save(self._collection)
        self._publish(PipelineGraphPointerUpdated(active.name, draft_pointer))
        self._publish(PipelineGraphDirtyChanged(active.name, active.is_dirty))
        self._invalidate_engine(active.name)
        return active

    def promote_all(self) -> list[PipelineUnit]:
        """Promote all draft graphs to finals; keep old finals on failure."""
        promoted: list[PipelineUnit] = []
        for pipeline in self._collection.list():
            pointer = pipeline.graph
            if pointer.status != GraphPointerStatus.DRAFT or not pointer.draft_path:
                continue
            try:
                promoted_pointer = self._storage.promote(pointer)
            except Exception as ex:
                log.exception("Failed to promote draft graph for pipeline '%s': %s", pipeline.name, ex)
                continue

            pipeline.update_graph(promoted_pointer)
            pipeline.clear_dirty()
            self._metadata_repo.save(self._collection)
            self._publish(PipelineGraphPointerUpdated(pipeline.name, promoted_pointer))
            self._publish(PipelineGraphDirtyChanged(pipeline.name, pipeline.is_dirty))
            log.info("Promoted pipeline '%s' draft to final %s", pipeline.name, promoted_pointer.final_path)
            self._invalidate_engine(pipeline.name)
            promoted.append(pipeline)
        return promoted

    def update_preview(self, image_path: Path) -> Optional[Path]:
        active = self._collection.active
        if not active:
            return None
        target_path = image_path
        if self._preview_port:
            target_path = self._preview_port.save_preview(active, image_path)
        active.set_preview(target_path)
        if self._preview_store:
            self._preview_store.set_preview(active.name, target_path)
        self._publish(PreviewImageChanged(active.name, target_path))
        return target_path

    def subscribe(self, event_type, handler) -> None:
        self._events.subscribe(event_type, handler)

    def _on_dirty_changed(self, is_dirty: bool) -> None:
        active = self._collection.active
        if not active:
            return
        active.is_dirty = is_dirty
        self._publish(PipelineGraphDirtyChanged(active.name, is_dirty))

    def _hydrate_preview(self, pipeline: PipelineUnit) -> None:
        if self._preview_store:
            stored = self._preview_store.get_preview(pipeline.name)
            pipeline.set_preview(stored)
        self._emit_preview_changed(pipeline)

    def _emit_preview_changed(self, pipeline: Optional[PipelineUnit]) -> None:
        name = pipeline.name if pipeline else None
        path = pipeline.preview_path if pipeline else None
        self._publish(PreviewImageChanged(name, path))

    def build_signature(self, pipeline_name: str) -> str:
        """Compute a lightweight signature for dirty detection."""
        pipeline = self._collection.get(pipeline_name)
        if not pipeline:
            raise KeyError(f"Pipeline '{pipeline_name}' not found")
        path = pipeline.graph.active_path()
        timestamp = None
        if path and path.exists():
            try:
                timestamp = path.stat().st_mtime_ns
            except Exception:
                timestamp = None
        stamp = timestamp if timestamp is not None else "missing"
        return f"{pipeline.name}:{stamp}"

    def run_pipeline(
        self,
        pipeline_name: str,
        images: list[Path],
        *,
        metadata: Optional[dict[str, Any]] = None,
        executor_params: Optional[dict[str, Any]] = None,
        engine_params: Optional[EngineParams] = None,
        context: Optional[PipelineExecutionContext] = None,
    ) -> PipelineExecutionResult:
        pipeline = self._collection.get(pipeline_name)
        if not pipeline:
            raise KeyError(f"Pipeline '{pipeline_name}' not found")

        graph_path = pipeline.graph.active_path()
        if graph_path is None:
            raise FileNotFoundError("Pipeline graph path is missing.")

        if pipeline.is_dirty and self._collection.active and self._collection.active.name == pipeline_name:
            self.save_active()
            pipeline = self._collection.get(pipeline_name) or pipeline
            graph_path = pipeline.graph.active_path()

        if graph_path is None or not graph_path.exists():
            raise FileNotFoundError(graph_path or Path("pipeline.pygraph"))

        if not self._engine:
            raise RuntimeError("Translation engine is not configured.")

        request = PipelineExecutionRequest(
            id=str(uuid.uuid4()),
            input=PipelineExecutionInput(images=images, metadata=metadata or {}),
            executor_params=executor_params or {},
            engine_params=engine_params,
            context=context,
        )
        return self._engine.run(pipeline_name, graph_path, request)

    def _publish(self, event) -> None:
        self._events.publish(event)

    def _cleanup_orphans(self) -> None:
        try:
            expected = {p.name for p in self._collection.list()}
            self._storage.cleanup_project_orphans(expected)
        except Exception:
            log.debug("Failed to cleanup pipeline orphans", exc_info=True)

    def cleanup_after_save(self) -> None:
        """Remove shared temp for current project after successful save/promotion."""
        try:
            self._storage.cleanup_current_shared_temp()
        except Exception:
            log.debug("Failed to cleanup shared temp after save", exc_info=True)

    def _load_graph_or_blank(self, pipeline: PipelineUnit) -> None:
        """Load the pipeline graph if available; fall back to blank with a warning."""
        path = pipeline.graph.active_path()
        if path is None:
            self._pyflow.new_blank()
            return

        if not path.exists():
            reason = f"Graph file missing at {path}"
            log.warning("Pipeline '%s' graph missing: %s", pipeline.name, path)
            self._publish(PipelineGraphLoadWarning(pipeline.name, path, reason))
            self._pyflow.new_blank()
            return

        try:
            self._pyflow.load_graph(path)  # type: ignore[arg-type]
        except Exception as ex:  # pragma: no cover - depends on PyFlow internals
            reason = f"Failed to load graph '{path}': {ex}"
            log.warning("Pipeline '%s' graph load failed: %s", pipeline.name, ex)
            self._publish(PipelineGraphLoadWarning(pipeline.name, path, reason))
            self._pyflow.new_blank()

    def _invalidate_engine(self, pipeline_name: str) -> None:
        if not self._engine:
            return
        try:
            self._engine.invalidate(pipeline_name)
        except Exception:
            log.debug("Failed to invalidate engine for pipeline '%s'", pipeline_name, exc_info=True)
