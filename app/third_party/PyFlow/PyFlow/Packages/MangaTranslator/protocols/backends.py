from __future__ import annotations

from typing import Any, Iterable, List, Protocol, Sequence, Tuple

# Typing helpers kept light to avoid importing heavy deps at protocol-definition time.
ImageType = Any
HierarchyType = Any


class TextDetectionBackend(Protocol):
    """Detects text regions and returns a hierarchy-like structure."""

    def detect(self, image: ImageType) -> HierarchyType:
        ...


class InpaintingBackend(Protocol):
    """Removes or masks detected text regions from an image."""

    def inpaint(self, image: ImageType, hierarchy: HierarchyType) -> ImageType:
        ...


class TextExtractionBackend(Protocol):
    """Extracts bounding boxes and text strings from detections."""

    def extract(
        self, image: ImageType, hierarchy: HierarchyType
    ) -> Tuple[List[Sequence[int]], List[str]]:
        ...


class TranslationBackend(Protocol):
    """Translates text payloads."""

    def translate(self, texts: Iterable[str]) -> List[str]:
        ...


class TextInsertionBackend(Protocol):
    """Inserts translated text into image regions."""

    def insert(
        self, image: ImageType, text_areas: Iterable[Sequence[int]], text_list: Iterable[str]
    ) -> ImageType:
        ...

