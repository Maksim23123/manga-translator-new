from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.application.pipelines.events import (
    ActivePipelineChanged,
    PipelineAdded,
    PipelineEventBus,
    PipelineGraphDirtyChanged,
    PipelineGraphPointerUpdated,
    PipelineListUpdated,
    PipelineRemoved,
    PipelineRenamed,
)
from app.application.pipelines.ports import GraphStoragePort, PipelineMetadataRepository, PipelinePreviewPort, PyFlowGateway
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.domain.pipelines.pipeline_collection import PipelineCollection
from app.domain.pipelines.pipeline_unit import PipelineUnit


class PipelineService:
    """Application service coordinating pipeline operations and PyFlow orchestration."""

    def __init__(
        self,
        *,
        metadata_repo: PipelineMetadataRepository,
        storage: GraphStoragePort,
        pyflow_gateway: PyFlowGateway,
        preview_port: Optional[PipelinePreviewPort] = None,
        event_bus: Optional[PipelineEventBus] = None,
    ) -> None:
        self._metadata_repo = metadata_repo
        self._storage = storage
        self._pyflow = pyflow_gateway
        self._preview_port = preview_port
        self._events = event_bus or PipelineEventBus()
        self._collection = PipelineCollection()

        self._pyflow.on_dirty_changed(self._on_dirty_changed)

    @property
    def collection(self) -> PipelineCollection:
        return self._collection

    def load(self) -> PipelineCollection:
        self._collection = self._metadata_repo.load()
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))

        active = self._collection.active
        if active:
            active_path = active.graph.active_path()
            if active_path:
                self._pyflow.load_graph(active_path)
            else:
                self._pyflow.new_blank()
            self._publish(ActivePipelineChanged(active.name))
        else:
            self._pyflow.new_blank()
            self._publish(ActivePipelineChanged(None))

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

        return pipeline

    def rename(self, old_name: str, new_name: str) -> PipelineUnit:
        pipeline = self._collection.rename(old_name, new_name)
        self._metadata_repo.save(self._collection)
        self._publish(PipelineRenamed(old_name=old_name, new_name=new_name))
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))
        return pipeline

    def remove(self, name: str) -> PipelineUnit:
        removed = self._collection.remove(name)
        self._metadata_repo.save(self._collection)
        self._publish(PipelineRemoved(name))
        self._publish(PipelineListUpdated([p.name for p in self._collection.list()]))

        if removed.graph.status != GraphPointerStatus.MISSING:
            self._storage.delete_graph(removed.graph)
        if self._preview_port:
            self._preview_port.delete_preview(removed)

        active = self._collection.active
        self._publish(ActivePipelineChanged(active.name if active else None))
        if active and active.graph.active_path():
            self._pyflow.load_graph(active.graph.active_path())  # type: ignore[arg-type]
        else:
            self._pyflow.new_blank()

        return removed

    def set_active(self, name: Optional[str]) -> Optional[PipelineUnit]:
        previous_active = self._collection.active
        if previous_active and previous_active.name != name and previous_active.is_dirty:
            self.save_active()

        active = self._collection.set_active(name)
        self._metadata_repo.save(self._collection)
        self._publish(ActivePipelineChanged(active.name if active else None))

        if active and active.graph.active_path():
            self._pyflow.load_graph(active.graph.active_path())  # type: ignore[arg-type]
        else:
            self._pyflow.new_blank()

        return active

    def save_active(self) -> Optional[PipelineUnit]:
        active = self._collection.active
        if not active:
            return None

        target_path = self._storage.draft_path_for(active.name)
        self._pyflow.save_graph(target_path)

        promoted_pointer = self._storage.promote(active.graph.mark_draft(target_path))
        active.update_graph(promoted_pointer)
        active.clear_dirty()

        self._metadata_repo.save(self._collection)
        self._publish(PipelineGraphPointerUpdated(active.name, promoted_pointer))
        self._publish(PipelineGraphDirtyChanged(active.name, active.is_dirty))
        return active

    def update_preview(self, image_path: Path) -> Optional[Path]:
        active = self._collection.active
        if not active or not self._preview_port:
            return None
        saved_preview = self._preview_port.save_preview(active, image_path)
        active.set_preview(saved_preview)
        return saved_preview

    def subscribe(self, event_type, handler) -> None:
        self._events.subscribe(event_type, handler)

    def _on_dirty_changed(self, is_dirty: bool) -> None:
        active = self._collection.active
        if not active:
            return
        active.is_dirty = is_dirty
        self._publish(PipelineGraphDirtyChanged(active.name, is_dirty))

    def _publish(self, event) -> None:
        self._events.publish(event)
