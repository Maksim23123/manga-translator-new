from __future__ import annotations

from typing import Iterable, List, Optional

from PyFlow.Packages.MangaTranslator.protocols import TranslationBackend

from .base import NodeLogicError
from .legacy_backends import LegacyTranslationBackend


class TranslationLogic:
    """Translates a sequence of strings."""

    def __init__(self, backend: Optional[TranslationBackend] = None) -> None:
        self._backend = backend or LegacyTranslationBackend()

    def run(self, text_list: Iterable[str]) -> List[str]:
        if text_list is None:
            raise NodeLogicError("Text input missing.")

        return self._backend.translate(text_list)
