from __future__ import annotations

from typing import Iterable, List

from .legacy_backends import LegacyTranslationBackend


class TranslationLogic(LegacyTranslationBackend):
    """Compatibility wrapper: the backend now serves as the logic class."""

    def run(self, text_list: Iterable[str]) -> List[str]:
        return self.translate(text_list)
