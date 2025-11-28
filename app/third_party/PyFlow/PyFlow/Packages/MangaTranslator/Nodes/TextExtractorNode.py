from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import Hierarchy, NodeLogicError, TextExtractionLogic, copy_image



class TextExtractorNode(NodeBase):
    def __init__(self, name):
        super(TextExtractorNode, self).__init__(name)

        self.text_extractor = TextExtractionLogic()

        self.image_inp_pin = self.createInputPin('Image', 'ImageArrayPin')
        self.hierarchy_inp_pin = self.createInputPin('Hierarchy', 'HierarchyPin')
        self.text_areas_out_pin = self.createOutputPin('Text areas', 'IntPin', structure=StructureType.Array)
        self.text_out_pin = self.createOutputPin('Text', 'StringPin', structure=StructureType.Array)

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ImageArrayPin')
        helper.addInputDataType('HierarchyPin')
        helper.addInputDataType('IntPin')
        helper.addInputDataType('StringPin')
        helper.addInputStruct(StructureType.Single)
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Array)
        helper.addOutputStruct(StructureType.Array)
        return helper

    @staticmethod
    def category():
        return 'Text extraction'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Extrcts text from image from areas marked by hierarchy."

    def compute(self, *args, **kwargs):
        image = self.image_inp_pin.getData()
        hierarchy = self.hierarchy_inp_pin.getData()
        if image is None:
            self.setError("Invalid image input.")
            return
        if hierarchy is None or not isinstance(hierarchy, Hierarchy):
            self.setError("Invalid hierarchy input.")
            return
        try:
            text_areas, original_text = self.text_extractor.run(copy_image(image), hierarchy)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return

        self.text_areas_out_pin.setData(text_areas)
        self.text_out_pin.setData(original_text)

