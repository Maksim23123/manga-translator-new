from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import QListWidget, QListWidgetItem

from app.interface_adapters.pipelines.controllers.pipeline_list_controller import PipelineListController
from app.interface_adapters.pipelines.controllers.pipeline_properties_controller import (
    PipelinePropertiesController,
)
from app.interface_adapters.pipelines.presenters.pipeline_list_presenter import PipelineListPresenter
from app.interface_adapters.pipelines.presenters.pipeline_properties_presenter import (
    PipelinePropertiesPresenter,
)
from app.interface_adapters.pipelines.views.pipeline_list_view import PipelineListView
from app.interface_adapters.pipelines.views.pipeline_properties_view import PipelinePropertiesView
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PipelinePropertiesDockTool import (
    PipelinePropertiesDockTool,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PipelinesListDockTool import (
    PipelinesListDockTool,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipeline_properties import (
    PipelineProperties,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipelines_list.pipelines_list import (
    PipelinesList,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipelines_list.pipelines_list_item import (
    PipelinesListItem,
)


class PipelinesListDockAdapter(PipelineListView):
    """Adapter that wires the PyFlow pipelines list dock to our controller/presenter layer."""

    def __init__(
        self,
        dock: PipelinesListDockTool,
        controller: PipelineListController | None = None,
        presenter: PipelineListPresenter | None = None,
    ) -> None:
        self._dock = dock
        self._controller = controller
        self._list: PipelinesList = dock.pipelines_list
        self._list_widget: QListWidget = self._list.pipelines_list_listWidget
        self._create_cb: Optional[Callable[[], None]] = None
        self._select_cb: Optional[Callable[[str], None]] = None
        self._delete_cb: Optional[Callable[[str], None]] = None
        self._suppress_selection = False

        self._list.new_pipeline_toolButton.clicked.connect(self._on_create_clicked)
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        if presenter:
            presenter.attach_view(self)

    # PipelineListView implementation
    def set_items(self, names: list[str], active_name: str | None) -> None:
        self._suppress_selection = True
        try:
            self._list_widget.clear()
            for name in names:
                item_widget = PipelinesListItem(name, is_active=name == active_name, parent=self._list)
                item_widget.deletePipelineTriggered.connect(self._handle_delete_clicked)

                item = QListWidgetItem(self._list_widget)
                item.setSizeHint(item_widget.sizeHint())
                self._list_widget.addItem(item)
                self._list_widget.setItemWidget(item, item_widget)

                if name == active_name:
                    self._list_widget.setCurrentItem(item)
        finally:
            self._suppress_selection = False

    def set_enabled(self, enabled: bool) -> None:
        self._list.setEnabled(enabled)
        self._list_widget.setEnabled(enabled)
        self._list.new_pipeline_toolButton.setEnabled(enabled)

    def on_create_requested(self, callback: Callable[[], None]) -> None:
        self._create_cb = callback

    def on_select_requested(self, callback: Callable[[str], None]) -> None:
        self._select_cb = callback

    def on_delete_requested(self, callback: Callable[[str], None]) -> None:
        self._delete_cb = callback

    # Internal helpers
    def _current_item_name(self) -> Optional[str]:
        item = self._list_widget.currentItem()
        if not item:
            return None
        widget = self._list_widget.itemWidget(item)
        if isinstance(widget, PipelinesListItem):
            return widget.item_name
        return None

    def _on_create_clicked(self) -> None:
        if self._controller:
            self._controller.create_pipeline()
            return
        if self._create_cb:
            self._create_cb()

    def _on_selection_changed(self) -> None:
        if self._suppress_selection:
            return
        selected_name = self._current_item_name()
        if not selected_name:
            return
        if self._controller:
            self._controller.select_pipeline(selected_name)
            return
        if self._select_cb:
            self._select_cb(selected_name)

    def _handle_delete_clicked(self, name: str) -> None:
        if self._controller:
            self._controller.delete_pipeline(name)
            return
        if self._delete_cb:
            self._delete_cb(name)


class PipelinePropertiesDockAdapter(PipelinePropertiesView):
    """Adapter that wires the PyFlow pipeline properties dock to our controller/presenter layer."""

    def __init__(
        self,
        dock: PipelinePropertiesDockTool,
        controller: PipelinePropertiesController | None = None,
        presenter: PipelinePropertiesPresenter | None = None,
    ) -> None:
        self._dock = dock
        self._controller = controller
        self._widget: PipelineProperties = dock.pipeline_properties
        self._name_cb: Optional[Callable[[str], None]] = None
        self._save_cb: Optional[Callable[[], None]] = None
        self._discard_cb: Optional[Callable[[], None]] = None
        self._suppress_name_signal = False

        self._widget.pipeline_name_lineEdit.textEdited.connect(self._on_name_edited)
        self._widget.save_changes_pushButton.clicked.connect(self._on_save_clicked)
        self._widget.discard_changes_pushButton.clicked.connect(self._on_discard_clicked)
        if presenter:
            presenter.attach_view(self)

    # PipelinePropertiesView implementation
    def show_pipeline(self, name: str | None) -> None:
        self._suppress_name_signal = True
        try:
            self._widget.pipeline_name_lineEdit.setText(name or "")
        finally:
            self._suppress_name_signal = False

    def set_enabled(self, enabled: bool) -> None:
        self._widget.setEnabled(enabled)
        self._widget.pipeline_name_lineEdit.setEnabled(enabled)
        self._widget.save_changes_pushButton.setEnabled(enabled)
        self._widget.discard_changes_pushButton.setEnabled(enabled)

    def on_name_changed(self, callback: Callable[[str], None]) -> None:
        self._name_cb = callback

    def on_save_requested(self, callback: Callable[[], None]) -> None:
        self._save_cb = callback

    def on_discard_requested(self, callback: Callable[[], None]) -> None:
        self._discard_cb = callback

    # Internal helpers
    def _on_name_edited(self, text: str) -> None:
        if self._suppress_name_signal:
            return
        if self._controller:
            self._controller.rename_active(text)
            return
        if self._name_cb:
            self._name_cb(text)

    def _on_save_clicked(self) -> None:
        if self._controller:
            self._controller.save_active()
            return
        if self._save_cb:
            self._save_cb()

    def _on_discard_clicked(self) -> None:
        if self._controller:
            self._controller.discard_changes()
            return
        if self._discard_cb:
            self._discard_cb()
