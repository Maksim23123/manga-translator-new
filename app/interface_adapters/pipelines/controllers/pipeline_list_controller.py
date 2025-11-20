from __future__ import annotations

from app.application.pipelines.pipeline_service import PipelineService


class PipelineListController:
    """Handles list dock actions and routes them into the pipeline service."""

    def __init__(self, *, service: PipelineService) -> None:
        self._service = service

    def create_pipeline(self) -> None:
        """Create a new pipeline using the default naming strategy."""
        self._service.create("Pipeline")

    def select_pipeline(self, name: str) -> None:
        self._service.set_active(name)

    def delete_pipeline(self, name: str) -> None:
        self._service.remove(name)
