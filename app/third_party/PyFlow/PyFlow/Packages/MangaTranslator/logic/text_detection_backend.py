from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

from .base import ImageType, NodeLogicError
from .hierarchy import Hierarchy

DEFAULT_API_KEYS_PATH = Path("app/config/api_keys.yaml")


def _load_api_key(api_keys_path: Path, key_name: str) -> str:
    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise NodeLogicError("Install `pyyaml` to load API keys.") from exc

    if not api_keys_path.exists():
        raise NodeLogicError(f"Missing API keys file: {api_keys_path}")
    try:
        content = api_keys_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content) or {}
        key = (data.get("api_keys") or {}).get(key_name)
    except Exception as exc:
        raise NodeLogicError(f"Failed to read API keys: {exc}") from exc
    if not key:
        raise NodeLogicError(f"API key '{key_name}' not found in {api_keys_path}")
    return key


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
        for bbox, cls_name in zip(detections.xyxy, detections.data.get("class_name", [])):
            boxes.append(
                {
                    "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                    "type": cls_name,
                }
            )
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


class TextDetectionBackend:
    """Detector that combines inference and EasyOCR output into a Hierarchy."""

    def __init__(self, api_keys_path: Path = DEFAULT_API_KEYS_PATH) -> None:
        self.api_keys_path = api_keys_path
        self._builder = _HierarchyBuilder()
        self._model = None
        self._easyocr_reader = None

    def detect(self, image: ImageType) -> Hierarchy:
        if image is None:
            raise NodeLogicError("Image input missing.")

        combined_boxes: List[dict] = []

        detections = self._run_inference(image)
        if detections is not None:
            combined_boxes.extend(self._builder.convert_supervision_to_boxes(detections))

        easyocr_boxes = self._run_easyocr(image)
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
            raise NodeLogicError(f"Failed to build detection hierarchy: {exc}") from exc

    # Helpers ------------------------------------------------------------------
    def _run_inference(self, image: Any) -> Any:
        model = self._ensure_model()
        try:
            results = model.infer(image)[0]
        except Exception as exc:
            raise NodeLogicError(f"Inference model failed: {exc}") from exc

        try:
            import supervision as sv  # type: ignore
        except Exception as exc:
            raise NodeLogicError("Install `supervision` to parse inference results.") from exc

        try:
            return sv.Detections.from_inference(results)
        except Exception as exc:
            raise NodeLogicError(f"Failed to parse inference results: {exc}") from exc

    def _run_easyocr(self, image: Any) -> List[Sequence[int]]:
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
            import easyocr  # type: ignore
        except Exception as exc:
            raise NodeLogicError("Install `numpy`, `opencv-python`, and `easyocr` to run detection.") from exc

        if not isinstance(image, np.ndarray):
            raise NodeLogicError("Detection requires numpy array image input.")

        if self._easyocr_reader is None:
            try:
                self._easyocr_reader = easyocr.Reader(["ja"])
            except Exception as exc:
                raise NodeLogicError(f"EasyOCR initialization failed: {exc}") from exc

        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = self._easyocr_reader.detect(rgb_image, link_threshold=5, text_threshold=0.3)
            return result[0][0] if result and result[0] else []
        except Exception as exc:
            raise NodeLogicError(f"EasyOCR detection failed: {exc}") from exc

    def _ensure_model(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from inference import get_model  # type: ignore
        except ModuleNotFoundError as exc:
            raise NodeLogicError("Install `inference` to enable text detection.") from exc

        model_kwargs = {"model_id": "manga-text-detection-xyvbw/2"}
        try:
            api_key = _load_api_key(self.api_keys_path, "inference_api_key")
            model_kwargs["api_key"] = api_key
        except NodeLogicError:
            # Missing key is allowed; inference SDK might work without it.
            pass

        try:
            self._model = get_model(**model_kwargs)
        except Exception as exc:
            raise NodeLogicError(f"Failed to load inference model: {exc}") from exc
        return self._model
