from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import (
    Hierarchy,
    NodeLogicError,
    TextDetectionBackend,
    copy_image,
)



class TextDetectorNode(NodeBase):
    def __init__(self, name):
        super(TextDetectorNode, self).__init__(name)

        self.text_detector = TextDetectionBackend()

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
            raw_hierarchy = self.text_detector.detect(copy_image(input_image))
            hierarchy = self._normalize_hierarchy(raw_hierarchy)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return
        self.hierarchy_out_pin.setData(hierarchy)

    @staticmethod
    def _normalize_hierarchy(hierarchy):
        if isinstance(hierarchy, Hierarchy):
            return hierarchy
        chunks = getattr(hierarchy, "text_chunks", None) or []
        boxes = getattr(hierarchy, "chunks_deepest_boxes", None) or []
        return Hierarchy(chunks_deepest_boxes=list(boxes), text_chunks=list(chunks))
