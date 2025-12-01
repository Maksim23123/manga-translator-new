from __future__ import annotations

from typing import Any, Optional

from PyFlow.Packages.MangaTranslator.protocols import TextDetectionBackend

from .base import NodeLogicError
from .hierarchy import Hierarchy
from .legacy_backends import LegacyTextDetectionBackend


class TextDetectionLogic:
    """Detects text regions inside an image."""

    def __init__(self, backend: Optional[TextDetectionBackend] = None) -> None:
        self._backend = backend or LegacyTextDetectionBackend()

    def run(self, image: Any) -> Hierarchy:
        if image is None:
            raise NodeLogicError("Image input missing.")

        hierarchy = self._backend.detect(image)
        return self._normalize_hierarchy(hierarchy)

    @staticmethod
    def _normalize_hierarchy(hierarchy: Any) -> Hierarchy:
        if isinstance(hierarchy, Hierarchy):
            return hierarchy
        chunks = getattr(hierarchy, "text_chunks", None) or []
        boxes = getattr(hierarchy, "chunks_deepest_boxes", None) or []
        return Hierarchy(chunks_deepest_boxes=list(boxes), text_chunks=list(chunks))
