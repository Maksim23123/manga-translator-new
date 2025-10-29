from qtpy import QtGui

from PyFlow.UI.Tool.Tool import DockTool
from ..manga_translator_api.gui.pipeline_properties import PipelineProperties
from ..manga_translator_api.controller.pipeline_properties_controller import PipelinePropertiesController


class PipelinePropertiesDockTool(DockTool):
    """docstring for History tool."""
    def __init__(self):
        super(PipelinePropertiesDockTool, self).__init__()

        self.pipeline_properties = PipelineProperties(self)
        self.setWidget(self.pipeline_properties)
        self.controller = PipelinePropertiesController(self.pipeline_properties)


    @staticmethod
    def getIcon():
        return None

    @staticmethod
    def toolTip():
        return "Displays properties of current active pipeline"

    @staticmethod
    def name():
        return "Pipeline Properties"
