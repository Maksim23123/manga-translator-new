from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from app.frameworks.pyside6_gui.tabs.tab import Tab
from app.interface_adapters.doc_units.controllers.doc_unit_controller import (
    DocUnitController,
)
from app.interface_adapters.doc_units.presenters.doc_unit_presenter import (
    DocUnitPresenter,
    DocUnitView,
    DocUnitViewModel,
)

from .details_view.details_view import DetailsView
from .unit_composer_ui import Ui_UnitComposer
from .unit_list.unit_list_item import UnitListItem


class DocUnitTab(Tab):
    _default_tab_name = "Doc Units"

    def __init__(
        self,
        presenter: DocUnitPresenter,
        controller: DocUnitController,
        parent: Optional[QMainWindow] = None,
    ) -> None:
        super().__init__(parent)
        self.set_tab_name(self._default_tab_name)

        self._presenter = presenter
        self._controller = controller

        self.ui = Ui_UnitComposer()
        self.ui.setupUi(self)

        self._details_view = DetailsView()
        self.ui.details_view_scrollArea.setWidget(self._details_view)

        self._unit_items: Dict[str, Tuple[QListWidgetItem, UnitListItem]] = {}
        self._is_dirty = False
        self._view_attached = False

        self._setup_connections()

    # region View interface implementation
    def display_units(self, units: List[DocUnitViewModel]) -> None:
        selection = self._current_selection()
        self._clear_unit_list()
        for view_model in units:
            self._add_unit_item(view_model, selection == view_model.unit_id)

    def highlight_active(self, unit_id: Optional[str]) -> None:
        for uid, (_, widget) in self._unit_items.items():
            widget.set_activity_status(uid == unit_id)
        if unit_id and unit_id in self._unit_items:
            self._select_unit_item(unit_id)
        elif unit_id is None:
            self._details_view.switch_display_mode(self._details_view.NONE_SELECTED_DISPLAY_MODE)

    def _select_unit_item(self, unit_id: str) -> None:
        item, _ = self._unit_items[unit_id]
        list_widget: QListWidget = self.ui.unitListWidget
        list_widget.blockSignals(True)
        list_widget.setCurrentItem(item)
        list_widget.blockSignals(False)
        self._display_unit_details(unit_id)

    def show_dirty_state(self, is_dirty: bool) -> None:
        self._is_dirty = is_dirty
        tab_text = f"{self._default_tab_name}*" if is_dirty else self._default_tab_name
        self.set_tab_name(tab_text)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)

    # endregion

    def on_project_available(self) -> None:
        if not self._view_attached:
            self._presenter.attach_view(self)
            self._view_attached = True
        else:
            self._presenter.refresh()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._view_attached:
            self._presenter.detach_view()
            self._view_attached = False
        super().closeEvent(event)

    def _setup_connections(self) -> None:
        self.ui.newUnitButton.clicked.connect(self._handle_create_unit)
        self.ui.importFilesPushButton.clicked.connect(self._handle_import_assets)
        self.ui.unitListWidget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.ui.unitListWidget.itemDoubleClicked.connect(self._handle_rename_requested)

    def _add_unit_item(self, view_model: DocUnitViewModel, selected: bool) -> None:
        list_widget: QListWidget = self.ui.unitListWidget
        item = QListWidgetItem(list_widget)
        unit_widget = UnitListItem(view_model, is_active=selected)
        item.setData(Qt.ItemDataRole.UserRole, view_model.unit_id)
        item.setSizeHint(unit_widget.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, unit_widget)
        if selected:
            list_widget.setCurrentItem(item)
        unit_widget.delete_button.clicked.connect(
            lambda _, uid=view_model.unit_id: self._handle_delete_unit(uid)
        )
        self._unit_items[view_model.unit_id] = (item, unit_widget)

    def _clear_unit_list(self) -> None:
        self.ui.unitListWidget.clear()
        self._unit_items.clear()

    def _handle_create_unit(self) -> None:
        name, ok = QInputDialog.getText(self, "Create Doc Unit", "Doc unit name:")
        if ok and name.strip():
            try:
                self._controller.create_doc_unit(name.strip())
            except Exception as exc:
                self.show_error(str(exc))

    def _handle_import_assets(self) -> None:
        unit_id = self._current_selection()
        if not unit_id:
            QMessageBox.information(self, "Import assets", "Select a doc unit first.")
            return
        source_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import asset",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)",
        )
        if source_path:
            try:
                self._controller.import_asset(unit_id, source_path)
            except Exception as exc:
                self.show_error(str(exc))

    def _handle_selection_changed(self) -> None:
        unit_id = self._current_selection()
        try:
            self._controller.set_active_doc_unit(unit_id)
        except Exception as exc:
            self.show_error(str(exc))
        if unit_id:
            self._display_unit_details(unit_id)

    def _handle_rename_requested(self, item: QListWidgetItem) -> None:
        unit_id = item.data(Qt.ItemDataRole.UserRole)
        if not unit_id:
            return
        current_name = ""
        if unit_id in self._unit_items:
            current_name = self._unit_items[unit_id][1].unit.name or ""
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Doc Unit",
            "New name:",
            text=current_name,
        )
        if ok and new_name.strip():
            try:
                self._controller.rename_doc_unit(unit_id, new_name.strip())
            except Exception as exc:
                self.show_error(str(exc))

    def _handle_delete_unit(self, unit_id: str) -> None:
        try:
            self._controller.delete_doc_unit(unit_id)
        except Exception as exc:
            self.show_error(str(exc))

    def _display_unit_details(self, unit_id: str) -> None:
        if unit_id not in self._unit_items:
            self._details_view.switch_display_mode(self._details_view.NONE_SELECTED_DISPLAY_MODE)
            return
        _, widget = self._unit_items[unit_id]
        self._details_view.switch_display_mode(self._details_view.UNIT_DISPLAY_MODE)
        details_widget = self._details_view.unit_details_widget
        details_widget.unit_name_lineEdit.setText(widget.unit.name)
        details_widget.unit_path_lineEdit.setText("")

    def _current_selection(self) -> Optional[str]:
        list_widget: QListWidget = self.ui.unitListWidget
        if current := list_widget.currentItem():
            return current.data(Qt.ItemDataRole.UserRole)
        return None
