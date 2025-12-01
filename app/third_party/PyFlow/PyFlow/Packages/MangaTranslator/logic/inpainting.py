from __future__ import annotations

from typing import Any

from .hierarchy import Hierarchy
from .legacy_backends import LegacyInpainterBackend


class InpainterLogic(LegacyInpainterBackend):
    """Compatibility wrapper: the backend now serves as the logic class."""

    def run(self, image: Any, hierarchy: Hierarchy) -> Any:
        return self.inpaint(image, hierarchy)
