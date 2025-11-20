from __future__ import annotations

from typing import Optional

from app.application.pipelines.events import PipelineListUpdated, PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService

from ..views.pipeline_list_view import PipelineListView


class PipelineListController:
    """Handles list dock actions and routes them into the pipeline service."""

    def __init__(self, *, service: PipelineService, event_bus: PipelineEventBus) -> None:
        self._service = service
        self._events = event_bus
        self._view: Optional[PipelineListView] = None

        self._events.subscribe(PipelineListUpdated, self._on_list_updated)

    def attach_view(self, view: PipelineListView) -> None:
        self._view = view
        view.on_create_requested(self._on_create_requested)
        view.on_select_requested(self._on_select_requested)
        view.on_delete_requested(self._on_delete_requested)

        names = [p.name for p in self._service.collection.list()]
        active = self._service.collection.active.name if self._service.collection.active else None
        view.set_items(names, active)
        view.set_enabled(True)

    def detach_view(self) -> None:
        self._view = None

    def _on_create_requested(self) -> None:
        # Delegates name collision handling to the service via add_with_name logic.
        self._service.create("Pipeline")

    def _on_select_requested(self, name: str) -> None:
        self._service.set_active(name)

    def _on_delete_requested(self, name: str) -> None:
        self._service.remove(name)

    def _on_list_updated(self, event: PipelineListUpdated) -> None:
        if not self._view:
            return
        active = self._service.collection.active.name if self._service.collection.active else None
        self._view.set_items(event.names, active)
