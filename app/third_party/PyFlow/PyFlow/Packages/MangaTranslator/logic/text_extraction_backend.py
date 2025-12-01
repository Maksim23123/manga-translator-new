from __future__ import annotations

from typing import Any, List, Sequence, Tuple

from .base import ImageType, NodeLogicError
from .hierarchy import Hierarchy


class TextExtractionBackend:
    """MangaOCR-based text extraction from detected regions."""

    def __init__(self, expansion_ratio: float = 0.8) -> None:
        self.expansion_ratio = expansion_ratio

    def extract(self, image: ImageType, hierarchy: Hierarchy) -> Tuple[List[Sequence[int]], List[str]]:
        text_chunks = list(getattr(hierarchy, "text_chunks", []) or [])
        if not text_chunks:
            return [], []

        try:
            import numpy as np  # type: ignore
            from PIL import Image  # type: ignore
            from manga_ocr import MangaOcr  # type: ignore
        except Exception as exc:
            raise NodeLogicError("Install `manga-ocr`, `Pillow`, and `numpy` for text extraction.") from exc

        if not isinstance(image, np.ndarray):
            raise NodeLogicError("Extraction requires numpy array image input.")

        ocr = MangaOcr()
        bbox_list: List[Sequence[int]] = []
        original_text_list: List[str] = []

        for obj in text_chunks:
            bbox = self._normalize_bbox(obj)
            if bbox is None:
                raise NodeLogicError("Invalid bbox in hierarchy.")
            crop = self._safe_crop(image, bbox)
            if crop is None:
                raise NodeLogicError("Failed to crop image for OCR.")
            crop_pil = Image.fromarray(crop)
            try:
                ocr_text = ocr(crop_pil)
            except Exception as exc:
                raise NodeLogicError(f"OCR failed: {exc}") from exc

            bbox_list.append(self._compute_zone(obj, bbox))
            original_text_list.append(str(ocr_text))

        return bbox_list, original_text_list

    # Helpers ------------------------------------------------------------------
    def _safe_crop(self, image: Any, bbox: Sequence[int]) -> ImageType:
        try:
            x_min, y_min, x_max, y_max = [int(x) for x in bbox]
        except Exception as exc:
            raise NodeLogicError("Invalid bbox values.") from exc
        if y_max <= y_min or x_max <= x_min:
            raise NodeLogicError("Invalid bbox dimensions.")
        try:
            return image[y_min:y_max, x_min:x_max]
        except Exception as exc:
            raise NodeLogicError(f"Failed to crop image: {exc}") from exc

    def _compute_zone(self, text_node: Any, bbox: Sequence[int]) -> List[int]:
        parent_bbox = text_node.get("parent_bbox") if isinstance(text_node, dict) else None
        if parent_bbox:
            nx_min, ny_min, nx_max, ny_max = bbox
            px_min, py_min, px_max, py_max = [int(x) for x in parent_bbox]
            x_center = (nx_min + nx_max) / 2
            y_center = (ny_min + ny_max) / 2
            x_exp = min(abs(x_center - px_min), abs(x_center - px_max)) * self.expansion_ratio
            y_exp = min(abs(y_center - py_min), abs(y_center - py_max)) * self.expansion_ratio
            return [
                int(x_center - x_exp),
                int(y_center - y_exp),
                int(x_center + x_exp),
                int(y_center + y_exp),
            ]
        return [int(x) for x in bbox]

    @staticmethod
    def _normalize_bbox(chunk: Any) -> Sequence[int] | None:
        if isinstance(chunk, dict) and "bbox" in chunk:
            return chunk["bbox"]
        bbox = getattr(chunk, "bbox", None) or getattr(chunk, "box", None)
        return bbox
