from __future__ import annotations

from typing import Any, Iterable, Sequence

from .legacy_backends import LegacyTextInsertionBackend


class TextInsertionLogic(LegacyTextInsertionBackend):
    """Compatibility wrapper: the backend now serves as the logic class."""

    def run(self, image: Any, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]) -> Any:
        return self.insert(image, text_areas, text_list)
