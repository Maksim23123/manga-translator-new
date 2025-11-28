from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Hierarchy:
    """Lightweight detection hierarchy container used by PyFlow nodes."""

    chunks_deepest_boxes: List[Any] = field(default_factory=list)
    text_chunks: List[Any] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.chunks_deepest_boxes and not self.text_chunks
