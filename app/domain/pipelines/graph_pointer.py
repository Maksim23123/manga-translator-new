from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class GraphPointerStatus(str, Enum):
    DRAFT = "draft"
    FINAL = "final"
    MISSING = "missing"


@dataclass(slots=True)
class GraphPointer:
    """Represents where a pipeline graph lives on disk."""

    final_path: Optional[Path]
    draft_path: Optional[Path] = None
    status: GraphPointerStatus = GraphPointerStatus.MISSING

    def active_path(self) -> Optional[Path]:
        if self.status == GraphPointerStatus.DRAFT:
            return self.draft_path
        if self.status == GraphPointerStatus.FINAL:
            return self.final_path
        return None

    def promote(self, final_path: Path) -> "GraphPointer":
        """Return a new pointer representing a promoted draft."""
        return GraphPointer(final_path=final_path, draft_path=None, status=GraphPointerStatus.FINAL)

    def mark_draft(self, draft_path: Path) -> "GraphPointer":
        """Return a new pointer pointing at a draft graph."""
        return GraphPointer(
            final_path=self.final_path,
            draft_path=draft_path,
            status=GraphPointerStatus.DRAFT,
        )
