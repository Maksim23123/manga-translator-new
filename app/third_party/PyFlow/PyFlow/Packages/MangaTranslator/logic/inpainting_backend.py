from __future__ import annotations

from typing import Any, Sequence

from .base import ImageType, NodeLogicError, copy_image
from .hierarchy import Hierarchy


class InpainterBackend:
    """OpenCV-based inpainting of detected regions."""

    def __init__(self, expand_px: int = 7) -> None:
        self.expand_px = expand_px

    def inpaint(self, image: ImageType, hierarchy: Hierarchy) -> ImageType:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception as exc:
            raise NodeLogicError("OpenCV/numpy are required for inpainting.") from exc

        if not isinstance(image, np.ndarray):
            raise NodeLogicError("Inpainting requires numpy array image input.")

        boxes = list(getattr(hierarchy, "chunks_deepest_boxes", []) or [])
        if not boxes:
            return copy_image(image)

        image_for_inpainting = image.copy()
        mask = np.zeros(image_for_inpainting.shape[:2], dtype=np.uint8)

        for box in boxes:
            try:
                x_min, y_min, x_max, y_max = box
            except Exception:
                raise NodeLogicError("Invalid bounding box for inpainting.")

            x_min_exp = max(int(x_min) - self.expand_px, 0)
            x_max_exp = min(int(x_max) + self.expand_px, image_for_inpainting.shape[1])
            y_min_exp = max(int(y_min) - self.expand_px, 0)
            y_max_exp = min(int(y_max) + self.expand_px, image_for_inpainting.shape[0])
            cv2.rectangle(mask, (x_min_exp, y_min_exp), (x_max_exp, y_max_exp), 255, -1)

        try:
            return cv2.inpaint(
                image_for_inpainting, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA
            )
        except Exception as exc:
            raise NodeLogicError(f"Inpainting failed: {exc}") from exc
