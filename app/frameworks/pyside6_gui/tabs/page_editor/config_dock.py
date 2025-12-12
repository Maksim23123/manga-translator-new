from __future__ import annotations

from typing import Callable, Iterable, Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDockWidget,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class PageConfigDock(QDockWidget):
    """Right-hand configuration dock for pipeline selection."""

    def __init__(self, parent=None) -> None:
        super().__init__("Settings", parent)
        self._combo = QComboBox(self)
        self._combo.setEditable(False)
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Pipeline", container))
        layout.addWidget(self._combo)
        layout.addStretch(1)
        container.setLayout(layout)
        self.setWidget(container)

    def set_pipeline_choices(self, choices: Iterable[str]) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        self._combo.addItems(list(choices))
        self._combo.blockSignals(False)

    def set_pipeline_value(self, value: Optional[str]) -> None:
        self._combo.blockSignals(True)
        if value:
            index = self._combo.findText(value)
            if index != -1:
                self._combo.setCurrentIndex(index)
            else:
                self._combo.setCurrentIndex(-1)
        else:
            self._combo.setCurrentIndex(-1)
        self._combo.blockSignals(False)

    def on_pipeline_changed(self, handler: Callable[[str], None]) -> None:
        self._combo.currentTextChanged.connect(handler)
