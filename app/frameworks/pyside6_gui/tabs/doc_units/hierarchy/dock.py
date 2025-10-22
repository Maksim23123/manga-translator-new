from __future__ import annotations

from typing import List, Optional, Sequence

from PySide6.QtCore import QItemSelectionModel, QModelIndex, QPoint, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QStyle, QTreeView

from app.frameworks.pyside6_gui.tabs.doc_units.hierarchy.tree_model import (
    HierarchyTreeModel,
)
from app.interface_adapters.doc_units.controllers.hierarchy_controller import (
    HierarchyController,
)
from app.interface_adapters.doc_units.presenters.hierarchy_presenter import (
    HierarchyNodeViewModel,
    HierarchyPresenter,
    HierarchyView,
)


NEW_FOLDER_DEFAULT_NAME = "New Chapter"


class HierarchyDock(HierarchyView):
    def __init__(
        self,
        tree_view: QTreeView,
        controller: HierarchyController,
        presenter: HierarchyPresenter,
    ) -> None:
        self._tree_view = tree_view
        self._controller = controller
        self._presenter = presenter
        self._expanded_ids: set[str] = set()
        self._pending_focus_ids: List[str] = []
        self._current_selection_id: Optional[str] = None
        self._suppress_selection_signal = False

        self._model = HierarchyTreeModel(
            rename_handler=self._on_rename_requested,
            move_handler=self._on_move_requested,
        )
        self._configure_tree_view()
        self._presenter.attach_view(self)

    def dispose(self) -> None:
        self._presenter.detach_view()

    # HierarchyView implementation
    def display_hierarchy(self, root: HierarchyNodeViewModel, changed_node_ids: List[str]) -> None:
        previous_selection = self._current_selection_id
        self._suppress_selection_signal = True
        try:
            self._model.update_tree(root)
            self._restore_expanded_nodes()
            candidate_ids = self._pending_focus_ids or changed_node_ids
            self._pending_focus_ids = []

            self._restore_selection(previous_selection, candidate_ids)
        finally:
            self._suppress_selection_signal = False

    def clear(self) -> None:
        self._model.clear()
        self._expanded_ids.clear()
        self._current_selection_id = None
        self._pending_focus_ids = []

    def select_node(self, node_id: Optional[str]) -> None:
        self._set_selection(node_id)

    # Internal helpers
    def _configure_tree_view(self) -> None:
        style = QApplication.style()
        folder_icon = style.standardIcon(QStyle.SP_DirIcon)
        image_icon = style.standardIcon(QStyle.SP_FileIcon)
        self._model.set_icons(folder_icon, image_icon)

        self._tree_view.setModel(self._model)
        self._tree_view.setHeaderHidden(True)
        self._tree_view.setSelectionMode(QTreeView.ExtendedSelection)
        self._tree_view.setSelectionBehavior(QTreeView.SelectRows)
        self._tree_view.setEditTriggers(QTreeView.DoubleClicked | QTreeView.EditKeyPressed)
        self._tree_view.setDragEnabled(True)
        self._tree_view.setAcceptDrops(True)
        self._tree_view.setDropIndicatorShown(True)
        self._tree_view.setDragDropMode(QTreeView.InternalMove)
        self._tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree_view.setExpandsOnDoubleClick(True)

        self._tree_view.customContextMenuRequested.connect(self._open_context_menu)
        self._tree_view.expanded.connect(self._on_item_expanded)
        self._tree_view.collapsed.connect(self._on_item_collapsed)
        selection_model = self._tree_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self._on_selection_changed)

    def _open_context_menu(self, position: QPoint) -> None:
        menu = QMenu(self._tree_view)
        index = self._tree_view.indexAt(position)
        node = self._model.node_from_index(index)

        create_action = QAction("Create Chapter", menu)
        create_action.triggered.connect(lambda: self._handle_create_folder(index))
        menu.addAction(create_action)

        delete_action = QAction("Delete", menu)
        delete_action.triggered.connect(self._handle_delete_selection)
        menu.addAction(delete_action)

        global_pos = self._tree_view.viewport().mapToGlobal(position)
        menu.exec(global_pos)

    def _handle_create_folder(self, index: QModelIndex) -> None:
        node = self._model.node_from_index(index)
        anchor_id = node.node_id if node else None
        placement = "child" if node is None or node.node_type == "folder" else "sibling"
        try:
            new_node = self._controller.create_folder(anchor_id, placement, NEW_FOLDER_DEFAULT_NAME)
            self._pending_focus_ids = [new_node.node_id]
        except Exception as exc:
            self._show_error(str(exc))

    def _handle_delete_selection(self) -> None:
        selection = self._tree_view.selectionModel().selectedRows()
        node_ids: List[str] = []
        for index in selection:
            node = self._model.node_from_index(index)
            if node:
                node_ids.append(node.node_id)
        if not node_ids:
            return
        try:
            self._controller.delete_nodes(node_ids)
        except Exception as exc:
            self._show_error(str(exc))

    def _on_item_expanded(self, index: QModelIndex) -> None:
        node = self._model.node_from_index(index)
        if node:
            self._expanded_ids.add(node.node_id)

    def _on_item_collapsed(self, index: QModelIndex) -> None:
        node = self._model.node_from_index(index)
        if node and node.node_id in self._expanded_ids:
            self._expanded_ids.remove(node.node_id)

    def _on_selection_changed(self, selected, deselected) -> None:  # noqa: ANN001
        if self._suppress_selection_signal:
            return
        indexes = self._tree_view.selectionModel().selectedRows()
        primary_index = indexes[0] if indexes else QModelIndex()
        node = self._model.node_from_index(primary_index)
        node_id = node.node_id if node else None
        self._current_selection_id = node_id
        try:
            self._controller.select_node(node_id)
        except Exception as exc:
            self._show_error(str(exc))

    def _restore_expanded_nodes(self) -> None:
        if not self._expanded_ids:
            return
        for node_id in list(self._expanded_ids):
            index = self._model.find_index_by_id(node_id)
            if index.isValid():
                self._tree_view.setExpanded(index, True)
            else:
                self._expanded_ids.discard(node_id)

    def _restore_selection(self, previous_selection: Optional[str], candidate_ids: Sequence[str]) -> None:
        target_id: Optional[str] = None
        if previous_selection:
            index = self._model.find_index_by_id(previous_selection)
            if index.isValid():
                target_id = previous_selection
        if not target_id:
            for candidate in candidate_ids:
                index = self._model.find_index_by_id(candidate)
                if index.isValid():
                    target_id = candidate
                    break
        self._set_selection(target_id)

    def _set_selection(self, node_id: Optional[str]) -> None:
        self._suppress_selection_signal = True
        selection_model = self._tree_view.selectionModel()
        if selection_model is None:
            self._suppress_selection_signal = False
            return

        selection_model.clearSelection()
        if node_id:
            index = self._model.find_index_by_id(node_id)
            if index.isValid():
                selection_model.select(
                    index,
                    QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows,
                )
                self._tree_view.setCurrentIndex(index)
                self._tree_view.scrollTo(index)
                self._current_selection_id = node_id
            else:
                self._current_selection_id = None
        else:
            self._current_selection_id = None
        self._suppress_selection_signal = False

    def _on_rename_requested(self, node_id: str, new_name: str) -> bool:
        try:
            self._controller.rename_node(node_id, new_name)
            self._pending_focus_ids = [node_id]
            return True
        except Exception as exc:
            self._show_error(str(exc))
            return False

    def _on_move_requested(self, node_ids: List[str], target_parent_id: str, insert_index: int, copy: bool) -> bool:
        try:
            self._controller.move_nodes(
                node_ids,
                target_parent_id,
                insert_index,
                as_copy=copy,
            )
            if not copy and node_ids:
                self._pending_focus_ids = [node_ids[0]]
            return True
        except Exception as exc:
            self._show_error(str(exc))
            return False

    def _show_error(self, message: str) -> None:
        QMessageBox.critical(self._tree_view, "Error", message)
