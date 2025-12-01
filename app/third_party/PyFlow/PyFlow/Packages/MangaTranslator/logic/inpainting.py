from __future__ import annotations

from typing import Any, Optional

from PyFlow.Packages.MangaTranslator.protocols import InpaintingBackend

from .base import NodeLogicError
from .hierarchy import Hierarchy
from .legacy_backends import LegacyInpainterBackend


class InpainterLogic:
    """Removes detected regions (e.g., text boxes) from an image."""

    def __init__(self, backend: Optional[InpaintingBackend] = None) -> None:
        self._backend = backend or LegacyInpainterBackend()

    def run(self, image: Any, hierarchy: Hierarchy) -> Any:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if hierarchy is None:
            raise NodeLogicError("Hierarchy input missing.")

        return self._backend.inpaint(image, hierarchy)
