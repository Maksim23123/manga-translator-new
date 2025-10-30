from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

try:
    from pipeline.inpainter import Inpainter
except ModuleNotFoundError:
    Inpainter = None  # type: ignore[assignment]

try:
    from pipeline.text_detector.hierarchy_builder.hierarchy import Hierarchy
except ModuleNotFoundError:
    class Hierarchy:  # type: ignore[override]
        chunks_deepest_boxes = []



class InpainterNode(NodeBase):
    def __init__(self, name):
        super(InpainterNode, self).__init__(name)

        self.inpainter = Inpainter() if Inpainter else None

        self.image_inp_pin = self.createInputPin('Image', 'ImageArrayPin')
        self.hierarchy_inp_pin = self.createInputPin('Hierarchy', 'HierarchyPin')
        self.inpainted_image_out_pin = self.createOutputPin('Inpainted', 'ImageArrayPin')

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ImageArrayPin')
        helper.addInputDataType('HierarchyPin')
        helper.addOutputDataType('ImageArrayPin')
        helper.addInputStruct(StructureType.Single)
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Inpainting'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        hierarchy = self.hierarchy_inp_pin.getData()
        input_image = self.image_inp_pin.getData()

        if self.inpainter is None:
            self.setError("Inpainter dependency unavailable.")
            return

        if (not input_image is None and not hierarchy is None
                and isinstance(hierarchy, Hierarchy)):
            inpainted_image = self.inpainter.inpaint_bboxes(input_image.copy(), hierarchy.chunks_deepest_boxes)

            self.inpainted_image_out_pin.setData(inpainted_image)
        else:
            self.setError(ValueError("Wrong node inputs."))
