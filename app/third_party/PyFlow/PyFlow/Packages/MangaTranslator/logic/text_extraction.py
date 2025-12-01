from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from PyFlow.Packages.MangaTranslator.protocols import TextExtractionBackend

from .base import NodeLogicError
from .hierarchy import Hierarchy
from .legacy_backends import LegacyTextExtractionBackend


class TextExtractionLogic:
    """Extracts text strings from detected regions."""

    def __init__(self, backend: Optional[TextExtractionBackend] = None) -> None:
        self._backend = backend or LegacyTextExtractionBackend()

    def run(self, image: Any, hierarchy: Hierarchy) -> Tuple[List[Sequence[int]], List[str]]:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if hierarchy is None:
            raise NodeLogicError("Hierarchy input missing.")

        text_areas, texts = self._backend.extract(image, hierarchy)
        if len(text_areas) != len(texts):
            raise NodeLogicError("Text areas/text length mismatch.")
        return text_areas, texts
