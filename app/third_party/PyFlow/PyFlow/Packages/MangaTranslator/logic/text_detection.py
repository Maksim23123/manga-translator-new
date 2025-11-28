from __future__ import annotations

from typing import Any

from .base import NodeLogicError
from .hierarchy import Hierarchy


class TextDetectionLogic:
    """Detects text regions inside an image."""

    def run(self, image: Any) -> Hierarchy:
        if image is None:
            raise NodeLogicError("Image input missing.")

        # Placeholder detection: return an empty hierarchy to keep the pipeline flowing.
        return Hierarchy()
