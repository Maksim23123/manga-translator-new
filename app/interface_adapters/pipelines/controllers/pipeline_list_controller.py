from __future__ import annotations

from app.application.pipelines.pipeline_service import PipelineService


class PipelineListController:
    """Handles list dock actions and routes them into the pipeline service."""

    def __init__(self, *, service: PipelineService) -> None:
        self._service = service

    def create_pipeline(self, name: str) -> None:
        """Create a new pipeline using a user-provided name."""
        self._service.create(name)

    def select_pipeline(self, name: str) -> None:
        self._service.set_active(name)

    def delete_pipeline(self, name: str) -> None:
        self._service.remove(name)
