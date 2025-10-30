from PyFlow.Core import PinBase
from PyFlow.Core.Common import *

try:
    from pipeline.text_detector.hierarchy_builder.hierarchy import Hierarchy
except ModuleNotFoundError:
    class Hierarchy:  # type: ignore[override]
        """Placeholder hierarchy container used when pipeline dependencies are missing."""
        pass



class HierarchyPin(PinBase):
    """Holds detection data like text areas and bubbles."""
    def __init__(self, name, parent, direction, **kwargs):
        super(HierarchyPin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(None)

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
        self.setData(None)
        return super().serialize()
