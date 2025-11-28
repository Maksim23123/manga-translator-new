import os

try:
    from core.core import Core
except ModuleNotFoundError:
    Core = None  # type: ignore[assignment]

from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *

from PyFlow.Packages.MangaTranslator.logic import ImageImportLogic, NodeLogicError



class PipelineInputImageNode(NodeBase):

    def __init__(self, name):
        super(PipelineInputImageNode, self).__init__(name)
        self.core = Core() if Core else None
        self.pyflow_interaction_manager = (
            self.core.pipelines_manager.pyflow_interaction_manager if self.core else None
        )

        self._image_path = (
            self.pyflow_interaction_manager.preview_image_path if self.pyflow_interaction_manager else None
        )

        self.image_importer = ImageImportLogic()

        self.image_out_pin = self.createOutputPin('Image', 'ImageArrayPin')

        self._connect_to_events()

        if self.check_path(self._image_path):
            self.import_image()
    

    def _connect_to_events(self):
        if not self.core:
            return
        pyflow_iteraction_manager_event_bus = (
            self.core.event_bus.pipeline_manager_event_bus.pyflow_iteraction_manager_event_bus
        )
        pyflow_iteraction_manager_event_bus.previewImagePathChanged.connect(self._on_preview_image_path_changed)


    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addOutputDataType('ImageArrayPin')
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Pipeline input'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."
    
    
    def _on_preview_image_path_changed(self, path):
        if self.check_path(path):
            self._image_path = path
            self.import_image()


    def check_path(self, path):
        return path and os.path.exists(path)
    

    def import_image(self):
        if not self.check_path(self._image_path):
            return
        try:
            image = self.image_importer.run(self._image_path)
        except NodeLogicError as exc:
            self.setError(str(exc))
            return
        self.image_out_pin.setData(image)


    def compute(self, *args, **kwargs):
        self.import_image()
