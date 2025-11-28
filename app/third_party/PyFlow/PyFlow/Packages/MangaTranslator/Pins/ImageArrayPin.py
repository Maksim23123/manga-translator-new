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
    """Holds an image payload (numpy/cv2 matrix or list fallback)."""

    def __init__(self, name, parent, direction, **kwargs):
        super(ImageArrayPin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(self._empty_image())

    @staticmethod
    def _empty_image():
        if np is not None:
            return np.zeros((0, 0, 3), dtype=np.uint8)
        return []

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
        original_default = self._defaultValue
        self.setData(None)
        self._defaultValue = None
        try:
            return super().serialize()
        finally:
            self._defaultValue = original_default
