from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from .base import NodeLogicError
from .hierarchy import Hierarchy


class TextExtractionLogic:
    """Extracts text strings from detected regions."""

    def run(self, image: Any, hierarchy: Hierarchy) -> Tuple[List[Sequence[int]], List[str]]:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if hierarchy is None:
            raise NodeLogicError("Hierarchy input missing.")

        text_areas: List[Sequence[int]] = []
        texts: List[str] = []

        for idx, chunk in enumerate(hierarchy.text_chunks or []):
            bbox = self._extract_bbox(chunk, idx)
            text = self._extract_text(chunk)
            text_areas.append(bbox)
            texts.append(text)

        return text_areas, texts

    @staticmethod
    def _extract_bbox(chunk: Any, idx: int) -> Sequence[int]:
        bbox = getattr(chunk, "bbox", None) or getattr(chunk, "box", None)
        if bbox:
            return bbox
        return (idx, idx, idx, idx)

    @staticmethod
    def _extract_text(chunk: Any) -> str:
        text = getattr(chunk, "text", None)
        if text is None:
            text = getattr(chunk, "content", "") or ""
        return str(text)
