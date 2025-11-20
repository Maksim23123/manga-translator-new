from __future__ import annotations

from typing import Optional

from app.application.pipelines.pipeline_service import PipelineService

from ..views.pipeline_preview_view import PipelinePreviewView


class PipelinePreviewController:
    """Handles preview refresh actions."""

    def __init__(self, *, service: PipelineService) -> None:
        self._service = service
        self._view: Optional[PipelinePreviewView] = None

    def attach_view(self, view: PipelinePreviewView) -> None:
        self._view = view
        view.on_refresh_requested(self._on_refresh_requested)

    def detach_view(self) -> None:
        self._view = None

    def _on_refresh_requested(self) -> None:
        # Placeholder: actual preview generation will live in PipelineService.
        active = self._service.collection.active
        if self._view and active:
            self._view.show_preview(active.preview_path)
