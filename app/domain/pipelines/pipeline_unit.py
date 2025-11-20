from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .graph_pointer import GraphPointer


@dataclass(slots=True)
class PipelineUnit:
    """Domain model for a pipeline entry."""

    name: str
    graph: GraphPointer
    is_dirty: bool = False
    preview_path: Optional[Path] = None

    def rename(self, new_name: str) -> None:
        cleaned = new_name.strip()
        if not cleaned:
            raise ValueError("Pipeline name cannot be empty")
        self.name = cleaned

    def update_graph(self, pointer: GraphPointer) -> None:
        self.graph = pointer

    def mark_dirty(self) -> None:
        self.is_dirty = True

    def clear_dirty(self) -> None:
        self.is_dirty = False

    def set_preview(self, path: Optional[Path]) -> None:
        self.preview_path = path
