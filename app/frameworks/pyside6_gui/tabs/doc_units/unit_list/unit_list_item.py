from PySide6.QtWidgets import QWidget

from app.interface_adapters.doc_units.presenters.doc_unit_presenter import (
    DocUnitViewModel,
)

from .unit_list_item_ui import Ui_UnitListItem


class UnitListItem(QWidget):
    NONE_ITEM_MESSAGE = "[undefined]"

    def __init__(self, unit: DocUnitViewModel, is_active: bool = False):
        super().__init__()
        self.unit = unit
        self._setup_ui()
        self._display_unit_data(is_active)

    def _setup_ui(self):
        self.ui = Ui_UnitListItem()
        self.ui.setupUi(self)

        self.unit_name_label = self.ui.unitNameLabel
        self.is_active_label = self.ui.isActiveLabel
        self.delete_button = self.ui.deleteUnitPushButton

    def set_activity_status(self, is_active: bool):
        if is_active:
            self.is_active_label.setText("active")
        else:
            self.is_active_label.setText("")

    def _display_unit_data(self, active_status: bool):
        if self.unit:
            self.unit_name_label.setText(self.unit.name or self.NONE_ITEM_MESSAGE)
            self.set_activity_status(active_status)
        else:
            self.unit_name_label.setText(self.NONE_ITEM_MESSAGE)
