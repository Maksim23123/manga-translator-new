from typing import Optional

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.frameworks.pyside6_gui.tabs.tab import Tab


class TestTab(Tab):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.set_tab_name("Test")
        self._init_ui()

    def _init_ui(self) -> None:
        content = QWidget(self)
        layout = QVBoxLayout(content)
        layout.addWidget(QLabel("Test tab content", parent=content))
        layout.addStretch()

        self.setCentralWidget(content)
