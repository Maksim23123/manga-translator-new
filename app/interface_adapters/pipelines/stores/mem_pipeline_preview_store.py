from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.application.pipelines.ports import PipelinePreviewStore


class MemPipelinePreviewStore(PipelinePreviewStore):
    """In-memory holder for pipeline preview image paths (session-scoped)."""

    def __init__(self) -> None:
        self._previews: dict[str, Optional[Path]] = {}

    def get_preview(self, name: str) -> Optional[Path]:
        return self._previews.get(name)

    def set_preview(self, name: str, path: Optional[Path]) -> None:
        self._previews[name] = path

    def clear(self, name: Optional[str] = None) -> None:
        if name is None:
            self._previews.clear()
            return
        self._previews.pop(name, None)
