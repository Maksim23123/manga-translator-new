from qtpy import QtGui

from PyFlow.UI.Tool.Tool import DockTool

from ..manga_translator_api.gui.pipelines_list.pipelines_list import PipelinesList
from ..manga_translator_api.controller.pipelines_list_controller import PipelinesListController



class PipelinesListDockTool(DockTool):
    """docstring for History tool."""
    def __init__(self):
        super(PipelinesListDockTool, self).__init__()
        self.pipelines_list = PipelinesList(self)

        self.setWidget(self.pipelines_list)
        self.pipelines_list_controller = PipelinesListController(self.pipelines_list)


    @staticmethod
    def getIcon():
        return None

    @staticmethod
    def toolTip():
        return "List of all available pipelines"

    @staticmethod
    def name():
        return "Pipelines list"
