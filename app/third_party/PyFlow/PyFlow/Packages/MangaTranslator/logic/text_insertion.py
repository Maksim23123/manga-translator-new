from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence

from PyFlow.Packages.MangaTranslator.protocols import TextInsertionBackend

from .base import NodeLogicError
from .legacy_backends import LegacyTextInsertionBackend


class TextInsertionLogic:
    """Inserts translated text back into an image."""

    def __init__(self, backend: Optional[TextInsertionBackend] = None) -> None:
        self._backend = backend or LegacyTextInsertionBackend()

    def run(self, image: Any, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]) -> Any:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if text_areas is None:
            raise NodeLogicError("Text areas input missing.")
        if text_list is None:
            raise NodeLogicError("Text input missing.")

        return self._backend.insert(image, text_areas, text_list)
