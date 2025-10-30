try:
    from core.core import Core
except ModuleNotFoundError:
    Core = None  # type: ignore[assignment]

try:
    from core.pipelines_manager.pipeline_unit import PipelineUnit
except ModuleNotFoundError:
    class PipelineUnit:  # type: ignore[override]
        name: str = ""

from ..gui.pipeline_properties import PipelineProperties



class PipelinePropertiesController:
    def __init__(self, popeline_properties_widget: PipelineProperties):
        self.core = Core() if Core else None
        self.event_bus = self.core.event_bus if self.core else None  # type: ignore[attr-defined]
        self.connected_pipeline = None
        self.pipeline_properties_widget = popeline_properties_widget

        self._connect_to_events()
        self._connect_controller()
        self._show_active_pipeline_data()
    

    def _connect_controller(self):
        self.pipeline_properties_widget.discard_changes_pushButton.clicked.connect(self._show_active_pipeline_data)
        self.pipeline_properties_widget.save_changes_pushButton.clicked.connect(self._on_save_pipeline_clicked)


    def _connect_to_events(self):
        if not self.event_bus:
            return
        self.event_bus.activeProjectChanged.connect(self._show_active_pipeline_data)  # type: ignore[attr-defined]
        self.event_bus.pipeline_manager_event_bus.activePipelineChanged.connect(self._show_active_pipeline_data)  # type: ignore[attr-defined]


    def _show_active_pipeline_data(self):
        if not self.core:
            self.connected_pipeline = None
            self._display_pipeline(None)
            return
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
