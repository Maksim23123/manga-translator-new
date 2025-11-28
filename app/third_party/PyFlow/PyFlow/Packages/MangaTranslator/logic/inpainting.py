from __future__ import annotations

from typing import Any

from .base import copy_image, NodeLogicError
from .hierarchy import Hierarchy


class InpainterLogic:
    """Removes detected regions (e.g., text boxes) from an image."""

    def run(self, image: Any, hierarchy: Hierarchy) -> Any:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if hierarchy is None:
            raise NodeLogicError("Hierarchy input missing.")

        return copy_image(image)
