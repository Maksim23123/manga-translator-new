from pathlib import Path
from typing import List, Optional, Sequence

from app.application.doc_units.events import ActiveDocUnitChanged, DocUnitEventBus
from app.application.page_editor.dto import ImageSelection
from app.application.pipelines.events import PipelineEventBus
from app.interface_adapters.page_editor.page_editor_presenter import PageEditorPresenter


class FakeService:
    def __init__(self, images: list[ImageSelection]) -> None:
        self._images = images

    def list_pipelines(self) -> list[str]:
        return []

    def resolve_selection(self, _selection_ids: Sequence[str]) -> list[ImageSelection]:
        return self._images


class FakeController:
    def __init__(self) -> None:
        self.view = None
        self.selection: List[str] = []

    def set_view(self, view) -> None:
        self.view = view

    def update_selection(self, selection_ids: Sequence[str]) -> None:
        self.selection = list(selection_ids)


class FakeView:
    def __init__(self) -> None:
        self.images: list[str] = []
        self.pipeline_choices: Optional[list[str]] = None
        self.pipeline_value: Optional[str] = None
        self.actions_state = {}
        self.mode: Optional[str] = None
        self.errors: list[str] = []

    def show_images(self, paths: list[str]) -> None:
        self.images = paths

    def clear_images(self) -> None:
        self.images = []

    def set_pipeline_choices(self, choices: list[str]) -> None:
        self.pipeline_choices = choices

    def set_pipeline_value(self, value: Optional[str]) -> None:
        self.pipeline_value = value

    def set_view_mode(self, mode: str) -> None:
        self.mode = mode

    def set_actions_enabled(self, *, has_active_unit: bool, has_selection: bool) -> None:
        self.actions_state = {"has_active_unit": has_active_unit, "has_selection": has_selection}

    def show_error(self, message: str) -> None:
        self.errors.append(message)


def test_presenter_view_mode_toggle_prefers_translated(tmp_path: Path) -> None:
    original = tmp_path / "orig.png"
    translated = tmp_path / "translated.png"
    original.write_bytes(b"orig")
    translated.write_bytes(b"translated")

    images = [
        ImageSelection(
            node_id="node-1",
            path=original,
            translated_path=translated,
            pipeline_id=None,
            last_pipeline_signature=None,
        )
    ]

    doc_bus = DocUnitEventBus()
    pipeline_bus = PipelineEventBus()
    service = FakeService(images)
    presenter = PageEditorPresenter(service, doc_bus, pipeline_bus)
    controller = FakeController()
    view = FakeView()

    doc_bus.publish(ActiveDocUnitChanged("unit-1"))

    presenter.attach_view(view, controller)
    assert view.images == [str(original)]
    assert view.mode == "original"

    presenter.set_view_mode("translated")
    assert view.images == [str(translated)]
    assert view.mode == "translated"

    presenter.set_view_mode("original")
    assert view.images == [str(original)]
    assert view.mode == "original"
