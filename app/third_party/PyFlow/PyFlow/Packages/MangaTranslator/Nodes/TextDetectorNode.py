from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from pipeline.text_detector.text_detector import TextDetector



class TextDetectorNode(NodeBase):
    def __init__(self, name):
        super(TextDetectorNode, self).__init__(name)

        self.text_detector = TextDetector()

        self.image_inp_pin = self.createInputPin('Image', 'ImageArrayPin')
        self.hierarchy_out_pin = self.createOutputPin('Hierarchy', 'HierarchyPin')

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ImageArrayPin')
        helper.addOutputDataType('HierarchyPin')
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Text detection'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        input_image = self.image_inp_pin.getData()
        if not input_image is None:
            hierarchy = self.text_detector.get_detection_hierarchy(input_image.copy())
            self.hierarchy_out_pin.setData(hierarchy)
        else:
            self.setError(ValueError("Invalid image input."))
