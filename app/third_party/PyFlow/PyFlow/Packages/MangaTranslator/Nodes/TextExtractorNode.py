from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

try:
    from pipeline.text_extractor import TextExtractor
except ModuleNotFoundError:
    TextExtractor = None  # type: ignore[assignment]

try:
    from pipeline.text_detector.hierarchy_builder.hierarchy import Hierarchy
except ModuleNotFoundError:
    class Hierarchy:  # type: ignore[override]
        text_chunks = []



class TextExtractorNode(NodeBase):
    def __init__(self, name):
        super(TextExtractorNode, self).__init__(name)

        self.text_extractor = TextExtractor() if TextExtractor else None

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
        if self.text_extractor is None:
            self.setError("Text extractor dependency unavailable.")
            return
        if (not image is None and not hierarchy is None
                and isinstance(hierarchy, Hierarchy)):
            text_areas, original_text = self.text_extractor.extract_text(image.copy()
                                                            , hierarchy.text_chunks)

            self.text_areas_out_pin.setData(text_areas)
            self.text_out_pin.setData(original_text)
        else:
            self.setError(ValueError("Wrong node inputs."))

