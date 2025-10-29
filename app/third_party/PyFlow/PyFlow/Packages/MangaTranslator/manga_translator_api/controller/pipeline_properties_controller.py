from core.core import Core
from core.pipelines_manager.pipeline_unit import PipelineUnit

from ..gui.pipeline_properties import PipelineProperties



class PipelinePropertiesController:
    def __init__(self, popeline_properties_widget: PipelineProperties):
        self.core = Core()
        self.event_bus = self.core.event_bus
        self.connected_pipeline = None
        self.pipeline_properties_widget = popeline_properties_widget

        self._connect_to_events()
        self._connect_controller()
    

    def _connect_controller(self):
        self.pipeline_properties_widget.discard_changes_pushButton.clicked.connect(self._show_active_pipeline_data)
        self.pipeline_properties_widget.save_changes_pushButton.clicked.connect(self._on_save_pipeline_clicked)


    def _connect_to_events(self):
        self.event_bus.activeProjectChanged.connect(self._show_active_pipeline_data)
        self.event_bus.pipeline_manager_event_bus.activePipelineChanged.connect(self._show_active_pipeline_data)


    def _show_active_pipeline_data(self):
        self.connected_pipeline = self.core.pipelines_manager.active_pipeline
        self._display_pipeline(self.connected_pipeline)
    

    def _on_save_pipeline_clicked(self):
        new_pipeline_name = self.pipeline_properties_widget.pipeline_name_lineEdit.text()
        if self.connected_pipeline:
            self.connected_pipeline.name = new_pipeline_name


    def _display_pipeline(self, pipeline: PipelineUnit|None):
        
        if pipeline:
            self.pipeline_properties_widget.pipeline_name_lineEdit.setText(pipeline.name)
        else:
            self.pipeline_properties_widget.pipeline_name_lineEdit.setText("")
