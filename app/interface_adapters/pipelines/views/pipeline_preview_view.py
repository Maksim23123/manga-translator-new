from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol


class PipelinePreviewView(Protocol):
    """View contract for showing a pipeline preview image."""

    def show_preview(self, path: Path | None) -> None: ...

    def on_refresh_requested(self, callback: Callable[[], None]) -> None: ...
