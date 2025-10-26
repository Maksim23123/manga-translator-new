from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional

from PySide6.QtCore import (
    QAbstractItemModel,
    QByteArray,
    QDataStream,
    QIODevice,
    QModelIndex,
    Qt,
    QMimeData,
)
from PySide6.QtGui import QIcon

from app.interface_adapters.doc_units.presenters.hierarchy_presenter import (
    HierarchyNodeViewModel,
)


MimeType = "application/x-doc-unit-hierarchy"


@dataclass(slots=True)
class _TreeItem:
    node: HierarchyNodeViewModel
    parent: Optional["_TreeItem"]
    children: List["_TreeItem"]

    def row(self) -> int:
        if not self.parent:
            return 0
        return self.parent.children.index(self)


class HierarchyTreeModel(QAbstractItemModel):
    def __init__(
        self,
        rename_handler: Callable[[str, str], bool],
        move_handler: Callable[[List[str], str, int, bool], bool],
        parent=None,
    ):
        super().__init__(parent)
        self._rename_handler = rename_handler
        self._move_handler = move_handler
        self._root_item: Optional[_TreeItem] = None
        self._items_by_id: Dict[str, _TreeItem] = {}
        self._folder_icon: Optional[QIcon] = None
        self._image_icon: Optional[QIcon] = None

    def set_icons(self, folder_icon: QIcon, image_icon: QIcon) -> None:
        self._folder_icon = folder_icon
        self._image_icon = image_icon

    def update_tree(self, root: HierarchyNodeViewModel) -> None:
        self.beginResetModel()
        self._items_by_id.clear()
        self._root_item = self._build_tree(root, None)
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._items_by_id.clear()
        self._root_item = None
        self.endResetModel()

    # region Qt model overrides
    def index(self, row: int, column: int, parent: QModelIndex) -> QModelIndex:
        if not self._root_item or column != 0:
            return QModelIndex()

        parent_item = parent.internalPointer() if parent.isValid() else self._root_item
        if not isinstance(parent_item, _TreeItem):
            return QModelIndex()
        if not 0 <= row < len(parent_item.children):
            return QModelIndex()
        child_item = parent_item.children[row]
        return self.createIndex(row, column, child_item)

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        item: _TreeItem = index.internalPointer()
        if not item.parent or item.parent == self._root_item:
            return QModelIndex()
        return self.createIndex(item.parent.row(), 0, item.parent)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if not self._root_item:
            return 0
        if not parent.isValid():
            return len(self._root_item.children)
        item: _TreeItem = parent.internalPointer()
        if item.node.node_type == "folder":
            return len(item.children)
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: ARG002
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not self._root_item:
            return None
        item: _TreeItem = index.internalPointer()
        node = item.node

        if role in (Qt.DisplayRole, Qt.EditRole):
            return node.name
        if role == Qt.DecorationRole and self._folder_icon and self._image_icon:
            return self._folder_icon if node.node_type == "folder" else self._image_icon
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        item: _TreeItem = index.internalPointer()
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled
        if item.node.node_type == "folder":
            flags |= Qt.ItemIsDropEnabled
        return flags

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole) -> bool:
        if role != Qt.EditRole or not index.isValid():
            return False
        item: _TreeItem = index.internalPointer()
        new_name = str(value).strip()
        if not new_name or new_name == item.node.name:
            return False
        try:
            result = self._rename_handler(item.node.node_id, new_name)
        except Exception:
            return False
        return bool(result)

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction | Qt.CopyAction

    def mimeTypes(self) -> List[str]:
        return [MimeType]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        stream = QByteArray()
        data_stream = QDataStream(stream, QIODevice.WriteOnly)
        node_ids: List[str] = []
        for index in indexes:
            if not index.isValid():
                continue
            item: _TreeItem = index.internalPointer()
            if item.node.node_id not in node_ids:
                node_ids.append(item.node.node_id)
        data_stream.writeInt32(len(node_ids))
        for node_id in node_ids:
            data_stream.writeString(node_id)
        mime_data.setData(MimeType, stream)
        return mime_data

    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent: QModelIndex,
    ) -> bool:
        if action == Qt.IgnoreAction:
            return True
        if column > 0 or MimeType not in data.formats():
            return False
        if not self._root_item:
            return False

        stream = QDataStream(data.data(MimeType), QIODevice.ReadOnly)
        count = stream.readInt32()
        node_ids: List[str] = []
        for _ in range(count):
            node_ids.append(stream.readString())

        target_item = parent.internalPointer() if parent.isValid() else self._root_item
        if not isinstance(target_item, _TreeItem):
            return False

        insert_row = row
        if insert_row == -1:
            insert_row = len(target_item.children)

        if target_item is self._root_item:
            target_parent_id = self._root_item.node.node_id
        else:
            target_parent_id = target_item.node.node_id

        try:
            return self._move_handler(node_ids, target_parent_id, insert_row, action == Qt.CopyAction)
        except Exception:
            return False

    # endregion

    def find_index_by_id(self, node_id: str) -> QModelIndex:
        item = self._items_by_id.get(node_id)
        if not item or item is self._root_item:
            return QModelIndex()
        path: List[int] = []
        current = item
        while current.parent and current.parent is not self._root_item:
            path.append(current.row())
            current = current.parent
        path.append(current.row())
        path.reverse()

        model_index = QModelIndex()
        parent_item = self._root_item
        for row in path:
            if parent_item is None or row >= len(parent_item.children):
                return QModelIndex()
            child_item = parent_item.children[row]
            model_index = self.createIndex(row, 0, child_item)
            parent_item = child_item
        return model_index

    def expanded_ids(self) -> List[str]:
        return [node_id for node_id, item in self._items_by_id.items() if item is not self._root_item and item.node.node_type == "folder"]

    def _build_tree(self, node: HierarchyNodeViewModel, parent: Optional[_TreeItem]) -> _TreeItem:
        item = _TreeItem(node=node, parent=parent, children=[])
        self._items_by_id[node.node_id] = item
        for child_model in node.children:
            child_item = self._build_tree(child_model, item)
            item.children.append(child_item)
        return item

    def node_from_index(self, index: QModelIndex) -> Optional[HierarchyNodeViewModel]:
        if not index.isValid():
            return None
        item: _TreeItem = index.internalPointer()
        return item.node if item else None

    def root_node_id(self) -> Optional[str]:
        if not self._root_item:
            return None
        return self._root_item.node.node_id
