from PyFlow.Core import PinBase
from PyFlow.Core.Common import *

import cv2
import numpy as np



class ImageArrayPin(PinBase):
    """doc string for DemoPin"""
    def __init__(self, name, parent, direction, **kwargs):
        super(ImageArrayPin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(np.zeros)

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
        return cv2.typing.MatLike

    @staticmethod
    def processData(data):
        return data
    
    def serialize(self):
        self.setData(None)
        return super().serialize()
