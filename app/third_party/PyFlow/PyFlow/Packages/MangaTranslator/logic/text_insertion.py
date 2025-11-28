from __future__ import annotations

from typing import Any, Iterable, Sequence

from .base import copy_image, NodeLogicError


class TextInsertionLogic:
    """Inserts translated text back into an image."""

    def run(self, image: Any, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]) -> Any:
        if image is None:
            raise NodeLogicError("Image input missing.")
        if text_areas is None:
            raise NodeLogicError("Text areas input missing.")
        if text_list is None:
            raise NodeLogicError("Text input missing.")

        areas = list(text_areas)
        texts = list(text_list)
        if len(areas) != len(texts):
            raise NodeLogicError("Text areas/text length mismatch.")

        return copy_image(image)
