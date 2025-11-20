from __future__ import annotations

from typing import Optional

from app.application.pipelines.events import ActivePipelineChanged, PipelineEventBus
from app.domain.pipelines.pipeline_collection import PipelineCollection

from ..views.pipeline_preview_view import PipelinePreviewView


class PipelinePreviewPresenter:
    """Keeps the preview dock in sync with the active pipeline preview path."""

    def __init__(self, *, event_bus: PipelineEventBus, collection: PipelineCollection) -> None:
        self._view: Optional[PipelinePreviewView] = None
        self._events = event_bus
        self._collection = collection

        self._events.subscribe(ActivePipelineChanged, self._on_active_changed)

    def attach_view(self, view: PipelinePreviewView) -> None:
        self._view = view
        self._hydrate()

    def detach_view(self) -> None:
        self._view = None

    def _hydrate(self) -> None:
        if not self._view:
            return
        active = self._collection.active
        self._view.show_preview(active.preview_path if active else None)

    def _on_active_changed(self, event: ActivePipelineChanged) -> None:
        if not self._view:
            return
        active = self._collection.active
        self._view.show_preview(active.preview_path if active else None)
