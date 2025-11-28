from __future__ import annotations

from typing import Iterable, List

from .base import NodeLogicError


class TranslationLogic:
    """Translates a sequence of strings."""

    def run(self, text_list: Iterable[str]) -> List[str]:
        if text_list is None:
            raise NodeLogicError("Text input missing.")

        return [f"[translated] {text}" for text in text_list]
