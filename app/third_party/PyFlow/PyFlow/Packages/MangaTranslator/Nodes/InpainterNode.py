from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import (
    Hierarchy,
    LegacyInpainterBackend,
    NodeLogicError,
    copy_image,
)



class InpainterNode(NodeBase):
    def __init__(self, name):
        super(InpainterNode, self).__init__(name)

        self.inpainter = LegacyInpainterBackend()

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

        if input_image is None:
            self.setError("Invalid image input.")
            return
        if hierarchy is None or not isinstance(hierarchy, Hierarchy):
            self.setError("Invalid hierarchy input.")
            return

        try:
            inpainted_image = self.inpainter.inpaint(copy_image(input_image), hierarchy)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return

        self.inpainted_image_out_pin.setData(inpainted_image)
