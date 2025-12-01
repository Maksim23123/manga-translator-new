from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from .hierarchy import Hierarchy
from .legacy_backends import LegacyTextExtractionBackend


class TextExtractionLogic(LegacyTextExtractionBackend):
    """Compatibility wrapper: the backend now serves as the logic class."""

    def run(self, image: Any, hierarchy: Hierarchy) -> Tuple[List[Sequence[int]], List[str]]:
        return self.extract(image, hierarchy)
