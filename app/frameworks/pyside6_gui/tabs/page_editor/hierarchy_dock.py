from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QItemSelectionModel, QModelIndex, Qt
from PySide6.QtWidgets import QApplication, QStyle, QTreeView

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


class PageHierarchyDock(HierarchyView):
    """Read-only hierarchy dock for the Page Editor."""

    def __init__(
        self,
        tree_view: QTreeView,
        presenter: HierarchyPresenter,
        controller: HierarchyController,
    ) -> None:
        self._tree_view = tree_view
        self._presenter = presenter
        self._controller = controller
        self._suppress_selection = False
        self._current_selection_ids: list[str] = []

        self._model = HierarchyTreeModel(
            rename_handler=lambda _node_id, _name: False,
            move_handler=lambda _ids, _parent, _index, _copy: False,
        )
        self._configure_tree_view()
        self._presenter.attach_view(self)

    def dispose(self) -> None:
        self._presenter.detach_view()

    # HierarchyView implementation
    def display_hierarchy(self, root: HierarchyNodeViewModel, changed_node_ids: List[str]) -> None:
        _ = changed_node_ids
        self._suppress_selection = True
        try:
            self._model.update_tree(root)
            self._restore_selection()
        finally:
            self._suppress_selection = False

    def clear(self) -> None:
        self._model.clear()
        self._current_selection_ids = []

    def select_nodes(self, primary_node_id: Optional[str], selected_node_ids: List[str]) -> None:
        self._suppress_selection = True
        try:
            selection_model = self._tree_view.selectionModel()
            if selection_model is None:
                return
            selection_model.clearSelection()
            self._current_selection_ids = list(dict.fromkeys(selected_node_ids))
            selection_flag = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
            for node_id in self._current_selection_ids:
                index = self._model.find_index_by_id(node_id)
                if index.isValid():
                    selection_model.select(index, selection_flag)
            if primary_node_id:
                index = self._model.find_index_by_id(primary_node_id)
                if index.isValid():
                    self._tree_view.setCurrentIndex(index)
                    self._tree_view.scrollTo(index)
        finally:
            self._suppress_selection = False

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
        self._tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self._tree_view.setDragEnabled(False)
        self._tree_view.setAcceptDrops(False)
        self._tree_view.setDropIndicatorShown(False)
        self._tree_view.setContextMenuPolicy(Qt.NoContextMenu)
        selection_model = self._tree_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self._on_selection_changed)

    def _restore_selection(self) -> None:
        if not self._current_selection_ids:
            return
        selection_model = self._tree_view.selectionModel()
        if not selection_model:
            return
        selection_flag = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        for node_id in self._current_selection_ids:
            index = self._model.find_index_by_id(node_id)
            if index.isValid():
                selection_model.select(index, selection_flag)

    def _on_selection_changed(self, selected, deselected) -> None:  # noqa: ANN001
        if self._suppress_selection:
            return
        selection_model = self._tree_view.selectionModel()
        if selection_model is None:
            return
        indexes = selection_model.selectedRows()
        selected_ids: List[str] = []
        for index in indexes:
            node = self._model.node_from_index(index)
            if node and node.node_id not in selected_ids:
                selected_ids.append(node.node_id)
        current_index = self._tree_view.currentIndex()
        primary_node_id: Optional[str] = None
        if current_index.isValid() and selection_model.isSelected(current_index):
            node = self._model.node_from_index(current_index)
            if node:
                primary_node_id = node.node_id
        if primary_node_id and primary_node_id not in selected_ids:
            selected_ids.insert(0, primary_node_id)
        if not primary_node_id and selected_ids:
            primary_node_id = selected_ids[0]

        self._current_selection_ids = selected_ids
        try:
            self._controller.select_node(primary_node_id, selected_ids)
        except Exception:
            # Keep UI responsive; errors surface through presenter/controller.
            return
