from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

try:
    from pipeline.text_inserter import TextInserter
except ModuleNotFoundError:
    TextInserter = None  # type: ignore[assignment]



class TextInserterNode(NodeBase):
    def __init__(self, name):
        super(TextInserterNode, self).__init__(name)

        self.text_inserter = TextInserter() if TextInserter else None

        self.image_inp_pin = self.createInputPin('Image', 'ImageArrayPin')
        self.text_areas_inp_pin = self.createInputPin('Text areas', 'IntPin', structure=StructureType.Array)
        self.text_inp_pin = self.createInputPin('Text', 'StringPin', structure=StructureType.Array)
        self.image_with_text_out_pin = self.createOutputPin('Image', 'ImageArrayPin')

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ImageArrayPin')
        helper.addInputDataType('IntPin')
        helper.addInputDataType('StringPin')
        helper.addOutputDataType('Image')
        helper.addInputStruct(StructureType.Single)
        helper.addInputStruct(StructureType.Array)
        helper.addInputStruct(StructureType.Array)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Text insertion'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        image = self.image_inp_pin.getData()
        text_ares = self.text_areas_inp_pin.getData()
        text = self.text_inp_pin.getData()

        if self.text_inserter is None:
            self.setError("Text inserter dependency unavailable.")
            return

        if image is None or text_ares is None or text is None:
            self.setError("Invalid input.")
            return

        image_with_text = self.text_inserter.insert_text_into_image(image.copy(), text_ares, text)

        self.image_with_text_out_pin.setData(image_with_text)
