from PyFlow.Core import PinBase
from PyFlow.Core.Common import *

try:
    import numpy as np
except ModuleNotFoundError:
    np = None  # type: ignore[assignment]

try:
    import cv2
    _MAT_TYPE = cv2.typing.MatLike
except ModuleNotFoundError:
    cv2 = None  # type: ignore[assignment]
    _MAT_TYPE = list



class ImageArrayPin(PinBase):
    """doc string for DemoPin"""
    def __init__(self, name, parent, direction, **kwargs):
        super(ImageArrayPin, self).__init__(name, parent, direction, **kwargs)
        default_value = np.zeros if np else lambda *args, **kwargs: []
        self.setDefaultValue(default_value)

    @staticmethod
    def IsValuePin():
        return True

    @staticmethod
    def supportedDataTypes():
        return ('ImageArrayPin',)

    @staticmethod
    def pinDataTypeHint():
        return 'ImageArrayPin', False

    @staticmethod
    def color():
        return (200, 200, 50, 255)

    @staticmethod
    def internalDataStructure():
        return _MAT_TYPE

    @staticmethod
    def processData(data):
        return data
    
    def serialize(self):
        self.setData(None)
        return super().serialize()
