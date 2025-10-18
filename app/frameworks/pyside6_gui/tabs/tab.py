from typing import Optional

from PySide6.QtWidgets import QMainWindow, QWidget


class Tab(QMainWindow):
    _default_tab_name = "Tab"

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._tab_name = self._default_tab_name

    @property
    def tab_name(self) -> str:
        return self._tab_name

    def set_tab_name(self, name: str) -> None:
        self._tab_name = name
