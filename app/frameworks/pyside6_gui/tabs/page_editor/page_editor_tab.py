from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from app.frameworks.pyside6_gui.tabs.page_editor.config_dock import PageConfigDock
from app.frameworks.pyside6_gui.tabs.page_editor.hierarchy_dock import PageHierarchyDock
from app.frameworks.pyside6_gui.tabs.page_editor.image_viewer import ImageListViewer
from app.frameworks.pyside6_gui.tabs.tab import Tab
from app.interface_adapters.page_editor.page_editor_controller import PageEditorController
from app.interface_adapters.page_editor.page_editor_presenter import PageEditorPresenter
from app.interface_adapters.doc_units.presenters.hierarchy_presenter import HierarchyPresenter
from app.interface_adapters.doc_units.controllers.hierarchy_controller import HierarchyController


class PageEditorTab(Tab):
    _default_tab_name = "Page Editor"

    def __init__(
        self,
        presenter: PageEditorPresenter,
        controller: PageEditorController,
        hierarchy_presenter: HierarchyPresenter,
        hierarchy_controller: HierarchyController,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.set_tab_name(self._default_tab_name)

        self._presenter = presenter
        self._controller = controller
        self._hierarchy_adapter: Optional[PageHierarchyDock] = None
        self._view_attached = False

        self._build_layout(hierarchy_presenter, hierarchy_controller)
        self._connect_signals()
        self.set_actions_enabled(has_active_unit=False, has_selection=False)

    # region View implementation
    def show_images(self, paths: list[str]) -> None:
        self._image_viewer.set_images(paths)

    def clear_images(self) -> None:
        self._image_viewer.clear_images()

    def set_pipeline_choices(self, choices: list[str]) -> None:
        self._config_dock.set_pipeline_choices(choices)

    def set_pipeline_value(self, value: Optional[str]) -> None:
        self._config_dock.set_pipeline_value(value)

    def set_actions_enabled(self, *, has_active_unit: bool, has_selection: bool) -> None:
        self._translate_all_button.setEnabled(has_active_unit)
        self._translate_dirty_button.setEnabled(has_active_unit)
        self._translate_selected_button.setEnabled(has_active_unit and has_selection)
        self._config_dock.setEnabled(has_active_unit and has_selection)
        if self._hierarchy_dock:
            self._hierarchy_dock.setEnabled(has_active_unit)

    def show_error(self, message: str) -> None:
        QMessageBox.critical(self, "Page Editor", message)

    # endregion

    def on_project_available(self) -> None:
        if not self._view_attached:
            self._presenter.attach_view(self, self._controller)
            self._view_attached = True
        else:
            self._presenter.refresh()

    def closeEvent(self, event) -> None:  # noqa: ANN001
        if self._view_attached:
            self._presenter.detach_view()
            self._view_attached = False
        if self._hierarchy_adapter:
            self._hierarchy_adapter.dispose()
        super().closeEvent(event)

    def _build_layout(
        self,
        hierarchy_presenter: HierarchyPresenter,
        hierarchy_controller: HierarchyController,
    ) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        self._translate_all_button = QPushButton("Translate All", central)
        self._translate_dirty_button = QPushButton("Translate Dirty", central)
        self._translate_selected_button = QPushButton("Translate Selected", central)

        top_bar = QHBoxLayout()
        top_bar.addWidget(self._translate_all_button)
        top_bar.addWidget(self._translate_dirty_button)
        top_bar.addWidget(self._translate_selected_button)
        top_bar.addStretch(1)

        layout.addLayout(top_bar)

        self._image_viewer = ImageListViewer(central)
        layout.addWidget(self._image_viewer, stretch=1)
        central.setLayout(layout)
        self.setCentralWidget(central)

        # Left hierarchy dock
        self._hierarchy_tree = QTreeView(self)
        self._hierarchy_adapter = PageHierarchyDock(
            self._hierarchy_tree,
            presenter=hierarchy_presenter,
            controller=hierarchy_controller,
        )
        self._hierarchy_dock = QDockWidget("Manga", self)
        self._hierarchy_dock.setWidget(self._hierarchy_tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._hierarchy_dock)

        # Right configuration dock
        self._config_dock = PageConfigDock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self._config_dock)

    def _connect_signals(self) -> None:
        self._translate_all_button.clicked.connect(self._controller.translate_all)
        self._translate_dirty_button.clicked.connect(self._controller.translate_dirty)
        self._translate_selected_button.clicked.connect(self._controller.translate_selected)
        self._config_dock.on_pipeline_changed(self._controller.apply_pipeline)
