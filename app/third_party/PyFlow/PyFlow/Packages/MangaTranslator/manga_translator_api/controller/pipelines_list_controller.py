from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, 
    QMainWindow, QMenuBar, QMenu, QTabWidget, QLabel, QListWidgetItem, QAbstractItemView, QMessageBox
)
from core.core import Core
from core.pipelines_manager.pipeline_unit import PipelineUnit
from ..gui.pipelines_list.pipelines_list import PipelinesList
from ..gui.pipelines_list.pipelines_list_item import PipelinesListItem
from ..gui.pipelines_list.new_pipeline_dialog import NewPipelineDialog



class PipelinesListController:

    EMPTY_ITEM_NAME = "[empty]"

    def __init__(self, pipelines_list: PipelinesList):
        self.pipelines_list = pipelines_list
        self.pipelines_listWidget = self.pipelines_list.pipelines_list_listWidget
        self.core = Core()
        self.pipelines_model = self.core.pipelines_manager.pipeline_data_model
        self.item_widget_list = list()

        self._connect_to_events()
        self._connect_controller()
        self.update_list_widget()


    def _connect_to_events(self):
        self.core.event_bus.activeProjectChanged.connect(self.update_list_widget)

        pipelines_model_event_bus = self.core.event_bus.pipeline_manager_event_bus.pipeline_data_model_event_bus

        pipelines_model_event_bus.pipelineAdded.connect(self._on_new_pipeline_added)
        pipelines_model_event_bus.pipelineRemoved.connect(self._on_pipeline_removed)
        pipelines_model_event_bus.pipelineUpdated.connect(self._on_pipeline_updated)
    

    def _connect_controller(self):
        self.pipelines_list.new_pipeline_toolButton.clicked.connect(self._on_new_pipeline_button_clicked)
        self.pipelines_list.pipelines_list_listWidget.itemSelectionChanged.connect(self._on_item_selection_changed)


    def update_list_widget(self):
        self.pipelines_list.pipelines_list_listWidget.clear()
        self.item_widget_list.clear()

        active_pipeline = self.core.pipelines_manager.active_pipeline

        if self.pipelines_model.initialized:
            for item_name in self.pipelines_model.get_pipeline_names_list():
                active = True if active_pipeline and active_pipeline.name == item_name else False
                self._add_list_item(item_name, active)


    def _add_list_item(self, item_name: str, is_active: bool=False):
        item_widget = PipelinesListItem(item_name, is_active, self.pipelines_list)
        item_widget.deletePipelineTriggered.connect(self._on_remove_button_clicked)

        # Create a placeholder item
        item = QListWidgetItem(self.pipelines_listWidget)
        item.setSizeHint(item_widget.sizeHint())

        def _on_active_unit_changed(new_active: PipelineUnit):
            if new_active:
                item_widget.set_active(item_widget.item_name == new_active.name)

        connection = self.core.event_bus.pipeline_manager_event_bus.activePipelineChanged.connect(_on_active_unit_changed)  

        item_widget.event_connection = connection

        self.item_widget_list.append(item_widget)

        self.pipelines_listWidget.addItem(item)
        self.pipelines_listWidget.setItemWidget(item, item_widget)

    
    def remove_list_item(self, index):
        item_widget = self.item_widget_list.pop(index)

        if isinstance(item_widget, PipelinesListItem):
            connection = item_widget.event_connection
            if connection:
                self.core.event_bus.pipeline_manager_event_bus.activePipelineChanged.disconnect(connection)
            
        item = self.pipelines_listWidget.takeItem(index)
        del item
    

    def _on_remove_button_clicked(self, pipeline_name: str):
        if not pipeline_name is None:
            try:
                success = self.pipelines_model.remove_pipeline(pipeline_name)
                if not success:
                    print("Failed to remove pipeline")
            except Exception as e:
                print(f"Error removing pipeline '{pipeline_name}': {e}")
    

    def _on_new_pipeline_button_clicked(self):
        new_pipeline_dialog = NewPipelineDialog(self.pipelines_list)

        result = new_pipeline_dialog.exec()

        if result and self.pipelines_model.initialized:
            new_pipeline_name = new_pipeline_dialog.pipeline_name
            try:
                self.pipelines_model.add_pipeline(new_pipeline_name)
            except Exception as e:
                QMessageBox.warning(self.pipelines_list, "Failed to create pipeline", str(e))


    def _on_new_pipeline_added(self):
        pipelines_names = self.pipelines_model.get_pipeline_names_list()

        if pipelines_names:
            self._add_list_item(pipelines_names[-1])
    

    def _on_pipeline_removed(self, pipeline: PipelineUnit):
        for i, item_widget in enumerate(self.item_widget_list):
            if (isinstance(item_widget, PipelinesListItem) 
                    and item_widget.item_name == pipeline.name):
                self.remove_list_item(i)
    

    def _on_pipeline_updated(self, index):
        new_name = self.pipelines_model.get_pipeline_names_list()[index]
        item_widget = self.item_widget_list[index]

        if item_widget and isinstance(item_widget, PipelinesListItem):
            item_widget.item_name = new_name 
    

    def _on_item_selection_changed(self):
        selected_items = self.pipelines_listWidget.selectedItems()

        if not selected_items:
            return
        
        selected_item = selected_items[0]

        item_widget = self.pipelines_listWidget.itemWidget(selected_item)

        if isinstance(item_widget, PipelinesListItem):
            self.core.pipelines_manager.set_active_pipeline(item_widget.item_name)
        else:
            raise Exception(f"Item widget expeted to be of a type '{PipelinesList.__name__}', got '{type(item_widget).__name__}'")

