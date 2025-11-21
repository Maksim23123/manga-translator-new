from __future__ import annotations

from app.application.pipelines.pipeline_service import PipelineService


class PipelinePropertiesController:
    """Handles property edits for the active pipeline."""

    def __init__(self, *, service: PipelineService) -> None:
        self._service = service

    def rename_active(self, name: str) -> None:
        active = self._service.collection.active
        if not active:
            return
        self._service.rename(active.name, name)

    def save_properties(self, name: str) -> None:
        """Persist staged property edits for the active pipeline."""
        active = self._service.collection.active
        if not active:
            return

        target_name = name.strip()
        if target_name and target_name != active.name:
            self._service.rename(active.name, target_name)

        self._service.save_active()

    def save_active(self) -> None:
        self._service.save_active()

    def discard_changes(self) -> None:
        """Refresh the active pipeline state on discard."""
        active = self._service.collection.active
        if active:
            self._service.set_active(active.name)
