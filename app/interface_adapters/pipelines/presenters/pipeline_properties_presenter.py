from __future__ import annotations

from typing import Callable, Optional

from app.application.pipelines.events import ActivePipelineChanged, PipelineRenamed, PipelineEventBus
from app.domain.pipelines.pipeline_collection import PipelineCollection

from ..views.pipeline_properties_view import PipelinePropertiesView


class PipelinePropertiesPresenter:
    """Keeps the properties dock in sync with the active pipeline."""

    def __init__(
        self,
        *,
        event_bus: PipelineEventBus,
        collection_provider: Callable[[], PipelineCollection],
    ) -> None:
        self._view: Optional[PipelinePropertiesView] = None
        self._events = event_bus
        self._collection_provider = collection_provider

        self._events.subscribe(ActivePipelineChanged, self._on_active_changed)
        self._events.subscribe(PipelineRenamed, self._on_pipeline_renamed)

    def attach_view(self, view: PipelinePropertiesView) -> None:
        self._view = view
        self._hydrate()

    def detach_view(self) -> None:
        self._view = None

    def _hydrate(self) -> None:
        if not self._view:
            return
        collection = self._collection_provider()
        active = collection.active
        self._view.show_pipeline(active.name if active else None)
        self._view.set_enabled(active is not None)

    def _on_active_changed(self, event: ActivePipelineChanged) -> None:
        if not self._view:
            return
        self._view.show_pipeline(event.name)
        self._view.set_enabled(event.name is not None)

    def _on_pipeline_renamed(self, event: PipelineRenamed) -> None:
        if not self._view:
            return
        collection = self._collection_provider()
        active = collection.active
        if active and active.name == event.new_name:
            self._view.show_pipeline(event.new_name)
