from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.application.pipelines.pipeline_service import PipelineService


@dataclass(slots=True)
class SelectPreviewImageRequest:
    image_path: Path


class SelectPreviewImage:
    """Sets the preview image for the active pipeline."""

    def __init__(self, service: PipelineService) -> None:
        self._service = service

    def execute(self, request: SelectPreviewImageRequest) -> Path:
        active = self._service.collection.active
        if not active:
            raise RuntimeError("No active pipeline selected.")

        if not request.image_path.exists():
            raise FileNotFoundError(request.image_path)

        updated = self._service.update_preview(request.image_path)
        if updated is None:
            raise RuntimeError("Failed to update preview image.")
        return updated
