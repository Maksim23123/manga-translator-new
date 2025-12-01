from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Tuple

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    yaml = None  # type: ignore[assignment]

from PyFlow.Packages.MangaTranslator.protocols import (
    InpaintingBackend,
    TextDetectionBackend,
    TextExtractionBackend,
    TextInsertionBackend,
    TranslationBackend,
)

from .base import ImageType, NodeLogicError, copy_image
from .hierarchy import Hierarchy


DEFAULT_API_KEYS_PATH = Path("app/config/api_keys.yaml")


def _load_api_key(api_keys_path: Path, key_name: str) -> Optional[str]:
    """Best-effort YAML key loader with guardrails for missing deps/files."""
    if yaml is None:
        return None
    if not api_keys_path.exists():
        return None
    try:
        content = api_keys_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        return (data.get("api_keys") or {}).get(key_name)
    except Exception:  # pragma: no cover - defensive
        return None


# --- Text detection -----------------------------------------------------------------------


class _Box:
    def __init__(self, bbox: Sequence[int], box_type: str) -> None:
        self.bbox = [int(x) for x in bbox]
        self.type = box_type
        self.children: List["_Box"] = []

    def can_be_child_of(self, parent_type: str) -> bool:
        if self.type == "text_area":
            return parent_type in ["clean_text", "messy_text", "text_bubble"]
        if self.type in ["clean_text", "messy_text"]:
            return parent_type == "text_bubble"
        if self.type == "text_bubble":
            return False
        return False

    def preferred_parent_order(self) -> List[str]:
        if self.type == "text_area":
            return ["clean_text", "messy_text", "text_bubble"]
        if self.type in ["clean_text", "messy_text"]:
            return ["text_bubble"]
        return []

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "bbox": [int(x) for x in self.bbox],
            "children": [child.to_dict() for child in self.children],
        }


class _HierarchyBuilder:
    """Subset of the legacy hierarchy builder used for detection output shaping."""

    @staticmethod
    def is_inside(parent_bbox: Sequence[int], child_bbox: Sequence[int], margin: float = 0.5) -> bool:
        px_min, py_min, px_max, py_max = [int(x) for x in parent_bbox]
        cx_min, cy_min, cx_max, cy_max = [int(x) for x in child_bbox]

        child_area = (cx_max - cx_min) * (cy_max - cy_min)

        ix_min = max(px_min, cx_min)
        iy_min = max(py_min, cy_min)
        ix_max = min(px_max, cx_max)
        iy_max = min(py_max, cy_max)

        if ix_min >= ix_max or iy_min >= iy_max:
            return False

        intersection_area = (ix_max - ix_min) * (iy_max - iy_min)
        return (intersection_area / child_area) >= margin

    def build_hierarchy(self, boxes: List[dict]) -> List[dict]:
        candidates = [_Box(bbox=box["bbox"], box_type=box["type"]) for box in boxes]

        def find_parent(candidate: _Box, potential_parents: List[_Box]) -> Optional[_Box]:
            for preferred_type in candidate.preferred_parent_order():
                best_parent = None
                for parent in potential_parents:
                    if parent.type != preferred_type:
                        continue
                    if not candidate.can_be_child_of(parent.type):
                        continue
                    if self.is_inside(parent.bbox, candidate.bbox):
                        for child in parent.children:
                            deeper_parent = find_parent(candidate, [child])
                            if deeper_parent:
                                return deeper_parent
                        best_parent = parent
                if best_parent:
                    return best_parent
            return None

        hierarchy: List[_Box] = []

        for candidate in candidates:
            parent = find_parent(candidate, hierarchy)
            if parent:
                parent.children.append(candidate)
            else:
                if candidate.type != "text_bubble":
                    parentless = find_parent(candidate, candidates)
                    if parentless:
                        parentless.children.append(candidate)
                        continue
                hierarchy.append(candidate)

        return [node.to_dict() for node in hierarchy]

    @staticmethod
    def convert_supervision_to_boxes(detections: Any) -> List[dict]:
        boxes: List[dict] = []
        try:
            for bbox, cls_name in zip(detections.xyxy, detections.data.get("class_name", [])):
                boxes.append(
                    {
                        "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                        "type": cls_name,
                    }
                )
        except Exception:
            # Fall back to empty list when detections structure is unexpected.
            return []
        return boxes

    @staticmethod
    def convert_easyocr_to_boxes(easyocr_boxes: Iterable[Sequence[int]]) -> List[dict]:
        boxes: List[dict] = []
        for box in easyocr_boxes:
            if len(box) < 4:
                continue
            x_min, x_max = min(box[0], box[1]), max(box[0], box[1])
            y_min, y_max = min(box[2], box[3]), max(box[2], box[3])
            boxes.append(
                {
                    "bbox": [int(x_min), int(y_min), int(x_max), int(y_max)],
                    "type": "text_area",
                }
            )
        return boxes


@dataclass
class _LegacyHierarchy:
    hierarchy: List[dict]

    def _collect_leaf_objects(self, hierarchy: List[dict]) -> List[dict]:
        collected: List[dict] = []

        def collect_from_node(node: dict, parent: Optional[dict] = None) -> None:
            new_node = node.copy()
            new_node["parent_bbox"] = (parent or {}).get("bbox") if parent else None
            if parent is not None and parent.get("type") == "text_bubble":
                collected.append(new_node)
            elif parent is None and node.get("type") in ["clean_text", "messy_text", "text_area"]:
                collected.append(new_node)
            for child in node.get("children", []):
                collect_from_node(child, node)

        for node in hierarchy:
            collect_from_node(node)

        return collected

    @property
    def text_chunks(self) -> List[dict]:
        if not hasattr(self, "_leaf_objects"):
            self._leaf_objects = self._collect_leaf_objects(self.hierarchy)
        return list(getattr(self, "_leaf_objects"))

    @property
    def chunks_deepest_boxes(self) -> List[Sequence[int]]:
        return self._extract_deepest_bboxes(self.hierarchy)

    def _extract_deepest_bboxes(self, hierarchy: List[dict]) -> List[Sequence[int]]:
        deepest: List[Sequence[int]] = []
        for node in hierarchy:
            children = node.get("children", [])
            if children:
                deepest.extend(self._extract_deepest_bboxes(children))
            else:
                bbox = node.get("bbox")
                if bbox is not None:
                    deepest.append(bbox)
        return deepest


class LegacyTextDetectionBackend(TextDetectionBackend):
    """Adapter around the legacy text detection stack (inference + EasyOCR)."""

    def __init__(self, api_keys_path: Path = DEFAULT_API_KEYS_PATH, allow_stub: bool = True) -> None:
        self.api_keys_path = api_keys_path
        self.allow_stub = allow_stub
        self._builder = _HierarchyBuilder()
        self._model = None
        self._easyocr_reader = None

    def detect(self, image: ImageType) -> Hierarchy:
        if image is None:
            raise NodeLogicError("Image input missing.")

        combined_boxes: List[dict] = []

        detections = self._safe_inference(image)
        if detections is not None:
            combined_boxes.extend(self._builder.convert_supervision_to_boxes(detections))

        easyocr_boxes = self._safe_easyocr(image)
        if easyocr_boxes:
            combined_boxes.extend(self._builder.convert_easyocr_to_boxes(easyocr_boxes))

        if not combined_boxes:
            return Hierarchy()

        try:
            hierarchy_dict = self._builder.build_hierarchy(combined_boxes)
            legacy_hierarchy = _LegacyHierarchy(hierarchy_dict)
            return Hierarchy(
                chunks_deepest_boxes=legacy_hierarchy.chunks_deepest_boxes,
                text_chunks=legacy_hierarchy.text_chunks,
            )
        except Exception as exc:
            if self.allow_stub:
                return Hierarchy()
            raise NodeLogicError(f"Failed to build detection hierarchy: {exc}") from exc

    # Helpers ------------------------------------------------------------------
    def _safe_inference(self, image: Any) -> Any:
        try:
            model = self._ensure_model()
        except NodeLogicError:
            if self.allow_stub:
                return None
            raise

        if model is None:
            return None

        try:
            results = model.infer(image)[0]
        except Exception as exc:
            if self.allow_stub:
                return None
            raise NodeLogicError(f"Inference model failed: {exc}") from exc

        try:
            import supervision as sv  # type: ignore

            return sv.Detections.from_inference(results)
        except Exception as exc:
            if self.allow_stub:
                return None
            raise NodeLogicError(f"Failed to parse inference results: {exc}") from exc

    def _safe_easyocr(self, image: Any) -> Optional[list]:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
            import easyocr  # type: ignore
        except Exception:
            return None if self.allow_stub else []

        if not hasattr(np, "ndarray") or not isinstance(image, np.ndarray):
            return None

        if self._easyocr_reader is None:
            try:
                self._easyocr_reader = easyocr.Reader(["ja"])
            except Exception as exc:
                if self.allow_stub:
                    return None
                raise NodeLogicError(f"EasyOCR initialization failed: {exc}") from exc

        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = self._easyocr_reader.detect(
                rgb_image, link_threshold=5, text_threshold=0.3
            )
            return result[0][0] if result and result[0] else []
        except Exception as exc:
            if self.allow_stub:
                return None
            raise NodeLogicError(f"EasyOCR detection failed: {exc}") from exc

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from inference import get_model  # type: ignore
        except ModuleNotFoundError as exc:
            raise NodeLogicError("Install `inference` to enable text detection.") from exc

        api_key = _load_api_key(self.api_keys_path, "inference_api_key")
        model_kwargs = {"model_id": "manga-text-detection-xyvbw/2"}
        if api_key:
            model_kwargs["api_key"] = api_key
        try:
            self._model = get_model(**model_kwargs)
        except Exception as exc:
            raise NodeLogicError(f"Failed to load inference model: {exc}") from exc
        return self._model


# --- Inpainting --------------------------------------------------------------------------


class LegacyInpainterBackend(InpaintingBackend):
    """Adapter around the legacy OpenCV-based inpainter."""

    def __init__(self, expand_px: int = 7, allow_stub: bool = True) -> None:
        self.expand_px = expand_px
        self.allow_stub = allow_stub

    def inpaint(self, image: ImageType, hierarchy: Hierarchy) -> ImageType:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception as exc:
            if self.allow_stub:
                return copy_image(image)
            raise NodeLogicError("OpenCV/numpy are required for inpainting.") from exc

        if not isinstance(image, np.ndarray):
            return copy_image(image)

        boxes = list(getattr(hierarchy, "chunks_deepest_boxes", []) or [])
        if not boxes:
            return copy_image(image)

        image_for_inpainting = image.copy()
        mask = np.zeros(image_for_inpainting.shape[:2], dtype=np.uint8)

        for box in boxes:
            try:
                x_min, y_min, x_max, y_max = box
            except Exception:
                continue

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
            if self.allow_stub:
                return copy_image(image)
            raise NodeLogicError(f"Inpainting failed: {exc}") from exc


# --- Text extraction ---------------------------------------------------------------------


class LegacyTextExtractionBackend(TextExtractionBackend):
    """Adapter around the legacy MangaOCR-based extractor."""

    def __init__(self, expansion_ratio: float = 0.8, allow_stub: bool = True) -> None:
        self.expansion_ratio = expansion_ratio
        self.allow_stub = allow_stub

    def extract(
        self, image: ImageType, hierarchy: Hierarchy
    ) -> Tuple[List[Sequence[int]], List[str]]:
        text_chunks = list(getattr(hierarchy, "text_chunks", []) or [])
        if not text_chunks:
            return [], []

        try:
            import numpy as np  # type: ignore
            from PIL import Image  # type: ignore
            from manga_ocr import MangaOcr  # type: ignore
        except Exception as exc:
            if self.allow_stub:
                return self._fallback(text_chunks)
            raise NodeLogicError("Install `manga-ocr`, `Pillow`, and `numpy` for text extraction.") from exc

        if not isinstance(image, np.ndarray):
            if self.allow_stub:
                return self._fallback(text_chunks)
            raise NodeLogicError("Extraction requires numpy array image input.")

        ocr = MangaOcr()
        bbox_list: List[Sequence[int]] = []
        original_text_list: List[str] = []

        for obj in text_chunks:
            bbox = self._normalize_bbox(obj)
            if bbox is None:
                continue
            crop = self._safe_crop(image, bbox)
            if crop is None:
                continue
            crop_pil = Image.fromarray(crop)
            try:
                ocr_text = ocr(crop_pil)
            except Exception as exc:
                if self.allow_stub:
                    ocr_text = ""
                else:
                    raise NodeLogicError(f"OCR failed: {exc}") from exc

            bbox_list.append(self._compute_zone(obj, bbox))
            original_text_list.append(str(ocr_text))

        return bbox_list, original_text_list

    # Helpers ------------------------------------------------------------------
    def _safe_crop(self, image: Any, bbox: Sequence[int]) -> Optional[Any]:
        try:
            x_min, y_min, x_max, y_max = [int(x) for x in bbox]
        except Exception:
            return None
        if y_max <= y_min or x_max <= x_min:
            return None
        try:
            return image[y_min:y_max, x_min:x_max]
        except Exception:
            return None

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
    def _normalize_bbox(chunk: Any) -> Optional[Sequence[int]]:
        if isinstance(chunk, dict) and "bbox" in chunk:
            return chunk["bbox"]
        bbox = getattr(chunk, "bbox", None) or getattr(chunk, "box", None)
        return bbox

    def _fallback(self, text_chunks: List[Any]) -> Tuple[List[Sequence[int]], List[str]]:
        bbox_list: List[Sequence[int]] = []
        texts: List[str] = []
        for idx, chunk in enumerate(text_chunks):
            bbox = self._normalize_bbox(chunk) or (idx, idx, idx, idx)
            text_value = ""
            if isinstance(chunk, dict):
                text_value = str(chunk.get("text") or chunk.get("content") or "")
            else:
                text_value = str(getattr(chunk, "text", "") or getattr(chunk, "content", ""))
            bbox_list.append(bbox)
            texts.append(text_value)
        return bbox_list, texts


# --- Translation ------------------------------------------------------------------------


class LegacyTranslationBackend(TranslationBackend):
    """Adapter around the legacy Together-powered translator."""

    def __init__(self, api_keys_path: Path = DEFAULT_API_KEYS_PATH, allow_stub: bool = True) -> None:
        self.api_keys_path = api_keys_path
        self.allow_stub = allow_stub
        self.system_prompt = (
            "You are a professional manga translator. Translate Japanese text into fluent, natural "
            "English while preserving tone, context, and flow. Return the same JSON array structure "
            "with an added 'translation' field and no extra commentary."
        )

    def translate(self, texts: Iterable[str]) -> List[str]:
        text_list = list(texts)
        if not text_list:
            return []

        api_key = _load_api_key(self.api_keys_path, "together_api_key")
        if api_key is None and self.allow_stub:
            return [self._fallback_translation(text) for text in text_list]
        try:
            from together import Together  # type: ignore
        except Exception as exc:
            if self.allow_stub:
                return [self._fallback_translation(text) for text in text_list]
            raise NodeLogicError("Install `together` to enable translation.") from exc

        try:
            client = Together(api_key=api_key)
        except Exception as exc:
            if self.allow_stub:
                return [self._fallback_translation(text) for text in text_list]
            raise NodeLogicError(f"Together client initialization failed: {exc}") from exc

        batch = self._prepare_batch(text_list)
        user_prompt = json.dumps(batch, ensure_ascii=False, indent=2)

        try:
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_response_text = response.choices[0].message.content
            translated_batch = json.loads(raw_response_text)
            return self._batch_to_list(translated_batch, len(text_list))
        except Exception as exc:
            if self.allow_stub:
                return [self._fallback_translation(text) for text in text_list]
            raise NodeLogicError(f"Translation failed: {exc}") from exc

    # Helpers ------------------------------------------------------------------
    @staticmethod
    def _prepare_batch(text_list: List[str]) -> List[dict]:
        return [{"id": idx, "original": entry} for idx, entry in enumerate(text_list) if str(entry).strip()]

    @staticmethod
    def _batch_to_list(translated_batch: List[dict], desired_size: int) -> List[str]:
        new_list = ["" for _ in range(desired_size)]
        for entry in translated_batch:
            try:
                index = int(entry.get("id", -1))
            except Exception:
                continue
            if 0 <= index < len(new_list):
                new_list[index] = str(entry.get("translation", ""))
        return new_list

    @staticmethod
    def _fallback_translation(text: str) -> str:
        return f"[translated] {text}"


# --- Text insertion ---------------------------------------------------------------------


class LegacyTextInsertionBackend(TextInsertionBackend):
    """Adapter around the legacy OpenCV-based text inserter."""

    def __init__(self, allow_stub: bool = True) -> None:
        self.allow_stub = allow_stub

    def insert(
        self, image: ImageType, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]
    ) -> ImageType:
        areas = list(text_areas)
        texts = list(text_list)
        if len(areas) != len(texts):
            raise NodeLogicError("Text areas/text length mismatch.")

        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception as exc:
            if self.allow_stub:
                return copy_image(image)
            raise NodeLogicError("OpenCV/numpy are required for text insertion.") from exc

        if not isinstance(image, np.ndarray):
            return copy_image(image)
        if not areas:
            return copy_image(image)

        image_with_text = image.copy()

        def zones_intersect(a: Sequence[int], b: Sequence[int]) -> bool:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)

        def shrink_zone(zone: Sequence[int], shrink_ratio: float) -> List[int]:
            x1, y1, x2, y2 = zone
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            w = (x2 - x1) * shrink_ratio / 2
            h = (y2 - y1) * shrink_ratio / 2
            return [int(cx - w), int(cy - h), int(cx + w), int(cy + h)]

        def resolve_overlaps(zones: List[Sequence[int]], max_iters: int = 20, shrink_step: float = 0.95) -> List[Sequence[int]]:
            n = len(zones)
            final_zones = list(zones)
            for _ in range(max_iters):
                conflict = False
                for i in range(n):
                    for j in range(i + 1, n):
                        if zones_intersect(final_zones[i], final_zones[j]):
                            final_zones[i] = shrink_zone(final_zones[i], shrink_step)
                            final_zones[j] = shrink_zone(final_zones[j], shrink_step)
                            conflict = True
                if not conflict:
                    break
            return final_zones

        def wrap_text(text: str, font, font_scale: float, thickness: int, box_width: int) -> List[str]:
            words = text.split()
            lines: List[str] = []
            line = ""
            for word in words:
                test_line = (line + " " + word).strip()
                width, _ = cv2.getTextSize(test_line, font, font_scale, thickness)[0]
                if width <= box_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    if cv2.getTextSize(word, font, font_scale, thickness)[0][0] > box_width:
                        lines.append(word)
                        line = ""
                    else:
                        line = word
            if line:
                lines.append(line)
            return lines

        def draw_wrapped_text_in_zone(
            img, text: str, zone: Sequence[int], font, base_scale: float, color, thickness: int
        ) -> None:
            x_min, y_min, x_max, y_max = zone
            box_width = x_max - x_min
            box_height = y_max - y_min

            font_scale = base_scale
            for _ in range(30):
                lines = wrap_text(text, font, font_scale, thickness, box_width)
                _, th = get_text_block_size(lines, font, font_scale, thickness)
                if lines:
                    tw = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
                else:
                    tw = 0
                if tw <= box_width and th <= box_height:
                    break
                font_scale *= 0.95
                if font_scale < 0.2:
                    break

            text_start_y = y_min + (box_height - th) // 2
            line_height = cv2.getTextSize("A", font, font_scale, thickness)[0][1] + 10
            for i, line in enumerate(lines):
                line_width = cv2.getTextSize(line, font, font_scale, thickness)[0][0]
                text_start_x = x_min + (box_width - line_width) // 2
                y = text_start_y + i * line_height
                cv2.putText(img, line, (text_start_x, y), font, font_scale, color, thickness, lineType=cv2.LINE_AA)

        def get_text_block_size(lines: List[str], font, font_scale: float, thickness: int) -> Tuple[int, int]:
            if not lines:
                return 0, 0
            (w, h), _ = cv2.getTextSize("A", font, font_scale, thickness)
            block_height = len(lines) * (h + 10)
            block_width = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines) if lines else 0
            return block_width, block_height

        font = cv2.FONT_HERSHEY_SIMPLEX
        base_font_scale = 1.0
        color = (255, 255, 255)
        thickness = 2

        non_overlapping_zones = resolve_overlaps(areas)
        base_image = image_with_text.copy() * 0

        for i, text in enumerate(texts):
            zone = non_overlapping_zones[i]
            draw_wrapped_text_in_zone(base_image, str(text), zone, font, base_font_scale, color, thickness)

        try:
            mask = base_image == 255
            image_with_text[mask] = 255 - image_with_text[mask]
        except Exception as exc:
            if self.allow_stub:
                return copy_image(image)
            raise NodeLogicError(f"Failed to blend inserted text: {exc}") from exc

        return image_with_text

