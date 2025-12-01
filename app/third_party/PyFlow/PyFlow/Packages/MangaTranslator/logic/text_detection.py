from __future__ import annotations

from typing import Any

from .hierarchy import Hierarchy
from .legacy_backends import LegacyTextDetectionBackend


class TextDetectionLogic(LegacyTextDetectionBackend):
    """Compatibility wrapper: the backend now serves as the logic class."""

    def run(self, image: Any) -> Hierarchy:
        hierarchy = self.detect(image)
        return self._normalize_hierarchy(hierarchy)

    @staticmethod
    def _normalize_hierarchy(hierarchy: Any) -> Hierarchy:
        if isinstance(hierarchy, Hierarchy):
            return hierarchy
        chunks = getattr(hierarchy, "text_chunks", None) or []
        boxes = getattr(hierarchy, "chunks_deepest_boxes", None) or []
        return Hierarchy(chunks_deepest_boxes=list(boxes), text_chunks=list(chunks))
