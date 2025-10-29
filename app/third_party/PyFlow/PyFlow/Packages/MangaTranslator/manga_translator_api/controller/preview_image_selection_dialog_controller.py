from ..gui.preview_image_selection_dialog import PreviewImageSelectionDialog

from core.core import Core
from core.unit_manager.unit import Unit
from controller.unit_composer_controller.unit_hierarchy.hierarchy_tree_view_model import HierarchyTreeViewModel



class PreviewImageSelectionDialogController:
    def __init__(self, dialog: PreviewImageSelectionDialog):
        self.dialog = dialog
        self.core = Core()
        self.selected_image_path = None

        self.dialog.accept_pushButton.setEnabled(False)
        
        self.model = HierarchyTreeViewModel(self.core)

        self.dialog.unit_content_treeView.setModel(self.model)
        self.dialog.unit_content_treeView.setHeaderHidden(True)
        active_unit = self.core.unit_manager.active_unit
        CURRENT_UNIT_NAME_LABEL_PREFIX = "Active manga: "
        if active_unit:
            self.dialog.current_unit_name_Label.setText(f"{CURRENT_UNIT_NAME_LABEL_PREFIX}{active_unit.unit_name}")
        else:
            self.dialog.current_unit_name_Label.setText(f"{CURRENT_UNIT_NAME_LABEL_PREFIX} [None]")
        self._set_model_data(active_unit)

        self._connect_controller()
    

    def _connect_controller(self):
        self.dialog.unit_content_treeView.clicked.connect(self._on_selection_changed)
        self.dialog.accept_pushButton.clicked.connect(self.dialog.accept)
        self.dialog.reject_pushButton.clicked.connect(self.dialog.reject)
    

    def _set_model_data(self, active_unit: Unit):
        if active_unit and active_unit.hierarchy_root:
            self.model.set_root_node(active_unit.hierarchy_root)
            self.dialog.unit_content_treeView.setModel(self.model)
        else:
            self.model.clear()
    

    def _on_selection_changed(self):
        selected_indexes = self.dialog.unit_content_treeView.selectedIndexes()

        if selected_indexes:
            selected_index = selected_indexes[0]
        else:
            return
        
        node = self.model.get_node(selected_index)

        if node.type == node.IMAGE_TYPE:
            self.selected_image_path = node.image_path
            self.dialog.accept_pushButton.setEnabled(True)
        else:
            self.dialog.accept_pushButton.setEnabled(False)

        