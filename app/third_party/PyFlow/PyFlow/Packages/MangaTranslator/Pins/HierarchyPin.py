from PyFlow.Core import PinBase
from PyFlow.Core.Common import *

try:
    from PyFlow.Packages.MangaTranslator.logic import Hierarchy
except Exception:  # pragma: no cover - defensive fallback
    try:
        from pipeline.text_detector.hierarchy_builder.hierarchy import Hierarchy  # type: ignore[misc]
    except ModuleNotFoundError:
        class Hierarchy:  # type: ignore[override]
            """Placeholder hierarchy container used when pipeline dependencies are missing."""
            chunks_deepest_boxes = []
            text_chunks = []


class HierarchyPin(PinBase):
    """Holds detection data like text areas and bubbles."""

    def __init__(self, name, parent, direction, **kwargs):
        super(HierarchyPin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(Hierarchy())

    @staticmethod
    def IsValuePin():
        return True

    @staticmethod
    def supportedDataTypes():
        return ('HierarchyPin',)

    @staticmethod
    def pinDataTypeHint():
        return 'HierarchyPin', False

    @staticmethod
    def color():
        return (200, 100, 50, 255)

    @staticmethod
    def internalDataStructure():
        return Hierarchy

    @staticmethod
    def processData(data):
        return data
    
    def serialize(self):
        original_default = self._defaultValue
        self.setData(None)
        self._defaultValue = None
        try:
            return super().serialize()
        finally:
            self._defaultValue = original_default
