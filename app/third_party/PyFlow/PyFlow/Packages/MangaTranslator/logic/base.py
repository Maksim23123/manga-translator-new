from __future__ import annotations

from typing import Any

ImageType = Any


class NodeLogicError(Exception):
    """Represents a recoverable error when executing node logic."""


def copy_image(image: ImageType) -> ImageType:
    """Return a shallow copy when possible to avoid mutating upstream data."""
    if hasattr(image, "copy"):
        try:
            return image.copy()
        except Exception:
            return image
    return image
