from __future__ import annotations

from typing import Optional

from app.application.pipelines.events import ActivePipelineChanged, PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService

from ..views.pipeline_properties_view import PipelinePropertiesView


class PipelinePropertiesController:
    """Handles property edits for the active pipeline."""

    def __init__(self, *, service: PipelineService, event_bus: PipelineEventBus) -> None:
        self._service = service
        self._events = event_bus
        self._view: Optional[PipelinePropertiesView] = None

        self._events.subscribe(ActivePipelineChanged, self._on_active_changed)

    def attach_view(self, view: PipelinePropertiesView) -> None:
        self._view = view
        view.on_name_changed(self._on_name_changed)
        view.on_save_requested(self._on_save_requested)
        view.on_discard_requested(self._on_discard_requested)
        self._hydrate()

    def detach_view(self) -> None:
        self._view = None

    def _hydrate(self) -> None:
        active = self._service.collection.active
        if not self._view:
            return
        self._view.show_pipeline(active.name if active else None)
        self._view.set_enabled(active is not None)

    def _on_active_changed(self, event: ActivePipelineChanged) -> None:
        self._hydrate()

    def _on_name_changed(self, name: str) -> None:
        active = self._service.collection.active
        if not active:
            return
        self._service.rename(active.name, name)

    def _on_save_requested(self) -> None:
        self._service.save_active()

    def _on_discard_requested(self) -> None:
        # Reload current graph or reset view state if needed; for now, just re-show.
        self._hydrate()
