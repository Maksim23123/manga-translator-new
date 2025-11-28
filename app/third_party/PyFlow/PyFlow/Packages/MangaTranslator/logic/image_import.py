from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

try:
    import cv2
except ModuleNotFoundError:
    cv2 = None  # type: ignore[assignment]

try:
    import numpy as np
except ModuleNotFoundError:
    np = None  # type: ignore[assignment]

from .base import ImageType, NodeLogicError


class ImageImportLogic:
    """Imports a preview image from disk."""

    def __init__(self, loader: Optional[Callable[[Path], ImageType]] = None) -> None:
        self._loader = loader or self._default_loader

    def run(self, path: str) -> ImageType:
        if not path:
            raise NodeLogicError("Preview image path is empty.")

        image_path = Path(path)
        if not image_path.exists():
            raise NodeLogicError(f"Preview image path not found: {image_path}")

        try:
            return self._loader(image_path)
        except NodeLogicError:
            raise
        except Exception as exc:  # pragma: no cover - defensive fallback
            raise NodeLogicError(f"Failed to import image: {exc}") from exc

    def _default_loader(self, path: Path) -> ImageType:
        if cv2 is not None:
            image = cv2.imread(str(path))
            if image is None:
                raise NodeLogicError(f"Unable to read image: {path}")
            return image

        if np is not None:
            data = path.read_bytes()
            return np.frombuffer(data, dtype=np.uint8)

        return list(path.read_bytes())
