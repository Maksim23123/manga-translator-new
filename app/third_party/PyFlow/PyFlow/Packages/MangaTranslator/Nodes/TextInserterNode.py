from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import NodeLogicError, TextInsertionLogic, copy_image



class TextInserterNode(NodeBase):
    def __init__(self, name):
        super(TextInserterNode, self).__init__(name)

        self.text_inserter = TextInsertionLogic()

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
        helper.addOutputDataType('ImageArrayPin')
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
        text_areas = self.text_areas_inp_pin.getData()
        text = self.text_inp_pin.getData()

        if image is None:
            self.setError("Invalid image input.")
            return
        if text_areas is None or text is None:
            self.setError("Invalid text inputs.")
            return

        try:
            image_with_text = self.text_inserter.run(copy_image(image), text_areas, text)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return

        self.image_with_text_out_pin.setData(image_with_text)
