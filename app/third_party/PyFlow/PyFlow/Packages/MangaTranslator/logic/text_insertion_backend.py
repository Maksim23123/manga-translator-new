from __future__ import annotations

from typing import Any, Iterable, List, Sequence, Tuple

from .base import ImageType, NodeLogicError, copy_image


class TextInsertionBackend:
    """OpenCV-based text inserter without stub fallbacks."""

    def insert(self, image: ImageType, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]) -> ImageType:
        areas = list(text_areas)
        texts = list(text_list)
        if len(areas) != len(texts):
            raise NodeLogicError("Text areas/text length mismatch.")

        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore
        except Exception as exc:
            raise NodeLogicError("OpenCV/numpy are required for text insertion.") from exc

        if not isinstance(image, np.ndarray):
            raise NodeLogicError("Text insertion requires numpy array image input.")
        if not areas:
            raise NodeLogicError("No text areas supplied for insertion.")

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
            raise NodeLogicError(f"Failed to blend inserted text: {exc}") from exc

        return image_with_text
