from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import Hierarchy, NodeLogicError, TextDetectionLogic, copy_image



class TextDetectorNode(NodeBase):
    def __init__(self, name):
        super(TextDetectorNode, self).__init__(name)

        self.text_detector = TextDetectionLogic()

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
        if input_image is None:
            self.setError("Invalid image input.")
            return
        try:
            hierarchy = self.text_detector.run(copy_image(input_image))
        except NodeLogicError as exc:
            self.setError(str(exc))
            return
        self.hierarchy_out_pin.setData(hierarchy)
