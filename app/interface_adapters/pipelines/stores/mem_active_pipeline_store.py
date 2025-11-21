from __future__ import annotations

from app.application.pipelines.ports import ActivePipelineStore


class MemActivePipelineStore(ActivePipelineStore):
    """In-memory holder for the active pipeline name."""

    def __init__(self) -> None:
        self._active: str | None = None

    def get_active(self) -> str | None:
        return self._active

    def set_active(self, name: str | None) -> None:
        self._active = name

    def clear(self) -> None:
        self._active = None
