from __future__ import annotations

from typing import List

import pytest
from PySide6.QtWidgets import QApplication

from app.frameworks.pyside6_gui.tabs.pipelines.dock_adapters import (
    PipelinePropertiesDockAdapter,
    PipelinesListDockAdapter,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipeline_properties import (
    PipelineProperties,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipelines_list.pipelines_list import (
    PipelinesList,
)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class _FakePipelinesListDock:
    def __init__(self) -> None:
        self.pipelines_list = PipelinesList()


class _FakePipelinePropertiesDock:
    def __init__(self) -> None:
        self.pipeline_properties = PipelineProperties()


class _RecordingPipelinePropertiesController:
    def __init__(self) -> None:
        self.rename_calls: List[str] = []
        self.saved_names: List[str] = []
        self.discard_calls: int = 0

    def rename_active(self, name: str) -> None:
        self.rename_calls.append(name)

    def save_properties(self, name: str) -> None:
        self.saved_names.append(name)

    def discard_changes(self) -> None:
        self.discard_calls += 1

    def save_active(self) -> None:  # pragma: no cover - maintained for compatibility
        pass


def test_pipelines_list_adapter_forwards_signals(qapp) -> None:  # noqa: ARG001
    dock = _FakePipelinesListDock()
    adapter = PipelinesListDockAdapter(dock, name_provider=lambda: "Created")  # type: ignore[arg-type]

    creates: List[str] = []
    selections: List[str] = []
    deletions: List[str] = []

    adapter.on_create_requested(lambda name: creates.append(name))
    adapter.on_select_requested(lambda name: selections.append(name))
    adapter.on_delete_requested(lambda name: deletions.append(name))

    adapter.set_items(["One", "Two"], "Two")

    dock.pipelines_list.new_pipeline_toolButton.click()
    assert creates == ["Created"]

    list_widget = dock.pipelines_list.pipelines_list_listWidget
    list_widget.setCurrentRow(0)
    assert selections == ["One"]

    first_widget = list_widget.itemWidget(list_widget.item(0))
    first_widget.deletePipelineTriggered.emit(first_widget.item_name)
    assert deletions == ["One"]

    adapter.set_enabled(False)
    assert not list_widget.isEnabled()
    assert not dock.pipelines_list.new_pipeline_toolButton.isEnabled()


def test_pipeline_properties_adapter_forwards_signals(qapp) -> None:  # noqa: ARG001
    dock = _FakePipelinePropertiesDock()
    adapter = PipelinePropertiesDockAdapter(dock)  # type: ignore[arg-type]

    names: List[str] = []
    saves: List[int] = []
    discards: List[int] = []

    adapter.on_name_changed(lambda name: names.append(name))
    adapter.on_save_requested(lambda: saves.append(1))
    adapter.on_discard_requested(lambda: discards.append(1))

    adapter.show_pipeline("Alpha")
    assert dock.pipeline_properties.pipeline_name_lineEdit.text() == "Alpha"
    assert names == []

    dock.pipeline_properties.pipeline_name_lineEdit.textEdited.emit("Beta")
    assert names == ["Beta"]

    dock.pipeline_properties.save_changes_pushButton.click()
    dock.pipeline_properties.discard_changes_pushButton.click()
    assert saves == [1]
    assert discards == [1]
    assert dock.pipeline_properties.pipeline_name_lineEdit.text() == "Alpha"

    adapter.set_enabled(False)
    assert not dock.pipeline_properties.isEnabled()
    assert not dock.pipeline_properties.save_changes_pushButton.isEnabled()
    assert not dock.pipeline_properties.discard_changes_pushButton.isEnabled()


def test_pipeline_properties_adapter_defers_rename_until_save(qapp) -> None:  # noqa: ARG001
    dock = _FakePipelinePropertiesDock()
    controller = _RecordingPipelinePropertiesController()
    adapter = PipelinePropertiesDockAdapter(dock, controller=controller)  # type: ignore[arg-type]

    adapter.show_pipeline("Alpha")

    dock.pipeline_properties.pipeline_name_lineEdit.textEdited.emit("Beta")
    assert controller.rename_calls == []
    assert controller.saved_names == []

    dock.pipeline_properties.save_changes_pushButton.click()
    assert controller.saved_names == ["Beta"]

    dock.pipeline_properties.pipeline_name_lineEdit.textEdited.emit("Gamma")
    dock.pipeline_properties.discard_changes_pushButton.click()
    assert controller.discard_calls == 1
    assert dock.pipeline_properties.pipeline_name_lineEdit.text() == "Beta"
