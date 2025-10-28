from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from app.frameworks.pyside6_gui.tabs.tab import Tab
from app.domain.doc_units.entities import HierarchyNode
from app.interface_adapters.doc_units.controllers.doc_unit_controller import (
    DocUnitController,
)
from app.interface_adapters.doc_units.controllers.hierarchy_controller import (
    HierarchyController,
)
from app.interface_adapters.doc_units.presenters.doc_unit_presenter import (
    DocUnitPresenter,
    DocUnitView,
    DocUnitViewModel,
)
from app.interface_adapters.doc_units.presenters.hierarchy_presenter import (
    HierarchyPresenter,
)
from app.interface_adapters.doc_units.presenters.hierarchy_details_presenter import (
    HierarchyDetailsPresenter,
    HierarchyDetailsView,
    HierarchyDetailsViewModel,
)

from .details_view.details_view import DetailsView
from .hierarchy.dock import HierarchyDock
from .unit_composer_ui import Ui_UnitComposer
from .unit_list.unit_list_item import UnitListItem


class DocUnitTab(Tab):
    _default_tab_name = "Doc Units"

    def __init__(
        self,
        presenter: DocUnitPresenter,
        controller: DocUnitController,
        hierarchy_presenter: HierarchyPresenter,
        hierarchy_controller: HierarchyController,
        hierarchy_details_presenter: HierarchyDetailsPresenter,
        parent: Optional[QMainWindow] = None,
    ) -> None:
        super().__init__(parent)
        self.set_tab_name(self._default_tab_name)

        self._presenter = presenter
        self._controller = controller
        self._hierarchy_details_presenter = hierarchy_details_presenter

        self.ui = Ui_UnitComposer()
        self.ui.setupUi(self)

        self._details_view = DetailsView()
        self.ui.details_view_scrollArea.setWidget(self._details_view)
        self._hierarchy_dock = HierarchyDock(
            self.ui.unitHierarchyTreeView,
            hierarchy_controller,
            hierarchy_presenter,
        )

        self._unit_items: Dict[str, Tuple[QListWidgetItem, UnitListItem]] = {}
        self._is_dirty = False
        self._view_attached = False
        self._details_current_unit_id: Optional[str] = None
        self._details_original_name: Optional[str] = None
        self._hierarchy_details_attached = False

        self._setup_connections()
        self._update_details_actions_state()

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
            self._reset_details_state()

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

    # HierarchyDetailsView implementation
    def show_hierarchy_item(self, view_model: HierarchyDetailsViewModel) -> None:
        widget = self._details_view.hierarchy_item_details_widget
        widget.item_name_lineEdit.setText(view_model.name)
        widget.item_type_lineEdit.setText(view_model.node_type)

        widget.children_number_widget.hide()
        widget.image_path_widget.hide()
        widget.image_preview_label.hide()
        widget.image_preview_label.clear()

        if view_model.node_type == HierarchyNode.FOLDER_TYPE:
            widget.children_number_widget.show()
            widget.children_number_lineEdit.setText(str(view_model.children_count or 0))
        else:
            image_path = view_model.image_path or ""
            widget.image_path_widget.show()
            widget.image_path_lineEdit.setText(image_path)
            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    image_width = pixmap.width()
                    image_height = pixmap.height() or 1
                    preview_height = max(1, int(self._details_view.width() * 0.4))
                    ratio = image_width / image_height
                    preview_width = max(1, int(preview_height * ratio))
                    widget.image_preview_label.setFixedSize(preview_width, preview_height)
                    widget.image_preview_label.setPixmap(pixmap)
                    widget.image_preview_label.setScaledContents(True)
                    widget.image_preview_label.show()
                else:
                    widget.image_preview_label.setText("Preview unavailable")
                    widget.image_preview_label.show()
            else:
                widget.image_preview_label.setText("Preview unavailable")
                widget.image_preview_label.show()

        self._details_view.switch_display_mode(self._details_view.HIERARCHY_ITEM_DISPLAY_MODE)

    def show_no_selection(self) -> None:
        widget = self._details_view.hierarchy_item_details_widget
        widget.item_name_lineEdit.clear()
        widget.item_type_lineEdit.clear()
        widget.children_number_lineEdit.clear()
        widget.image_path_lineEdit.clear()
        widget.image_preview_label.clear()
        widget.image_preview_label.hide()
        widget.image_path_widget.hide()
        widget.children_number_widget.hide()
        if not self._details_view.unit_details_widget.isVisible():
            self._details_view.switch_display_mode(self._details_view.NONE_SELECTED_DISPLAY_MODE)

    def on_project_available(self) -> None:
        try:
            self._controller.set_active_doc_unit(None)
        except Exception as exc:
            self.show_error(str(exc))
        if not self._view_attached:
            self._presenter.attach_view(self)
            self._view_attached = True
        else:
            self._presenter.refresh()
        if not self._hierarchy_details_attached:
            self._hierarchy_details_presenter.attach_view(self)
            self._hierarchy_details_attached = True
        self._update_details_actions_state()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self._view_attached:
            self._presenter.detach_view()
            self._view_attached = False
        if self._hierarchy_details_attached:
            self._hierarchy_details_presenter.detach_view()
            self._hierarchy_details_attached = False
        self._hierarchy_dock.dispose()
        super().closeEvent(event)

    def _setup_connections(self) -> None:
        self.ui.newUnitButton.clicked.connect(self._handle_create_unit)
        self.ui.importFilesPushButton.clicked.connect(self._handle_import_assets)
        self.ui.unitListWidget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.ui.unitListWidget.itemDoubleClicked.connect(self._handle_rename_requested)
        details_widget = self._details_view.unit_details_widget
        details_widget.save_changes_pushButton.clicked.connect(self._handle_save_details)
        details_widget.discard_changes_pushButton.clicked.connect(self._handle_discard_details)
        details_widget.unit_name_lineEdit.textChanged.connect(
            lambda _: self._update_details_actions_state()
        )

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
            self._reset_details_state()
            return
        _, widget = self._unit_items[unit_id]
        self._details_view.switch_display_mode(self._details_view.UNIT_DISPLAY_MODE)
        details_widget = self._details_view.unit_details_widget
        self._details_current_unit_id = unit_id
        self._details_original_name = widget.unit.name
        details_widget.unit_name_lineEdit.blockSignals(True)
        details_widget.unit_name_lineEdit.setText(widget.unit.name)
        details_widget.unit_name_lineEdit.blockSignals(False)
        details_widget.unit_path_lineEdit.setText("")
        self._update_details_actions_state()

    def _current_selection(self) -> Optional[str]:
        list_widget: QListWidget = self.ui.unitListWidget
        if current := list_widget.currentItem():
            return current.data(Qt.ItemDataRole.UserRole)
        return None

    def _handle_save_details(self) -> None:
        if not self._details_current_unit_id:
            return
        details_widget = self._details_view.unit_details_widget
        new_name = details_widget.unit_name_lineEdit.text().strip()
        if not new_name:
            self.show_error("Doc unit name must not be empty.")
            details_widget.unit_name_lineEdit.blockSignals(True)
            details_widget.unit_name_lineEdit.setText(self._details_original_name or "")
            details_widget.unit_name_lineEdit.blockSignals(False)
            self._update_details_actions_state()
            return
        if self._details_original_name and new_name == self._details_original_name:
            self._update_details_actions_state()
            return
        try:
            self._controller.rename_doc_unit(self._details_current_unit_id, new_name)
            self._details_original_name = new_name
            details_widget.unit_name_lineEdit.blockSignals(True)
            details_widget.unit_name_lineEdit.setText(new_name)
            details_widget.unit_name_lineEdit.blockSignals(False)
        except Exception as exc:
            self.show_error(str(exc))
            details_widget.unit_name_lineEdit.blockSignals(True)
            details_widget.unit_name_lineEdit.setText(self._details_original_name or "")
            details_widget.unit_name_lineEdit.blockSignals(False)
        finally:
            self._update_details_actions_state()

    def _handle_discard_details(self) -> None:
        if not self._details_current_unit_id:
            return
        details_widget = self._details_view.unit_details_widget
        details_widget.unit_name_lineEdit.blockSignals(True)
        details_widget.unit_name_lineEdit.setText(self._details_original_name or "")
        details_widget.unit_name_lineEdit.blockSignals(False)
        self._update_details_actions_state()

    def _update_details_actions_state(self) -> None:
        details_widget = self._details_view.unit_details_widget
        has_selection = self._details_current_unit_id is not None
        current_text = details_widget.unit_name_lineEdit.text().strip()
        original = (self._details_original_name or "").strip() if self._details_original_name else ""
        has_changes = has_selection and current_text != original
        can_save = has_changes and bool(current_text)
        details_widget.save_changes_pushButton.setEnabled(can_save)
        details_widget.discard_changes_pushButton.setEnabled(has_changes)

    def _reset_details_state(self) -> None:
        self._details_current_unit_id = None
        self._details_original_name = None
        details_widget = self._details_view.unit_details_widget
        details_widget.unit_name_lineEdit.blockSignals(True)
        details_widget.unit_name_lineEdit.setText("")
        details_widget.unit_name_lineEdit.blockSignals(False)
        details_widget.unit_path_lineEdit.setText("")
        self._update_details_actions_state()
