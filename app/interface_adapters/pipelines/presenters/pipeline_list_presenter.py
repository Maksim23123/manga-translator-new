from __future__ import annotations

from typing import Optional

from app.application.pipelines.events import ActivePipelineChanged, PipelineListUpdated, PipelineEventBus
from app.domain.pipelines.pipeline_collection import PipelineCollection

from ..views.pipeline_list_view import PipelineListView


class PipelineListPresenter:
    """Projects pipeline list state onto the list view."""

    def __init__(self, *, event_bus: PipelineEventBus, collection: PipelineCollection) -> None:
        self._view: Optional[PipelineListView] = None
        self._events = event_bus
        self._collection = collection

        self._events.subscribe(PipelineListUpdated, self._on_list_updated)
        self._events.subscribe(ActivePipelineChanged, self._on_active_changed)

    def attach_view(self, view: PipelineListView) -> None:
        self._view = view
        self._hydrate()

    def detach_view(self) -> None:
        self._view = None

    def _hydrate(self) -> None:
        if not self._view:
            return
        active = self._collection.active.name if self._collection.active else None
        self._view.set_items([p.name for p in self._collection.list()], active)
        self._view.set_enabled(True)

    def _on_list_updated(self, event: PipelineListUpdated) -> None:
        if not self._view:
            return
        active = self._collection.active.name if self._collection.active else None
        self._view.set_items(event.names, active)

    def _on_active_changed(self, event: ActivePipelineChanged) -> None:
        if not self._view:
            return
        names = [p.name for p in self._collection.list()]
        self._view.set_items(names, event.name)
