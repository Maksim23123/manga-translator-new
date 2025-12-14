from __future__ import annotations

from typing import Optional, Protocol, Sequence

from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    HierarchyLoaded,
    HierarchySelectionChanged,
    HierarchyUpdated,
)
from app.application.page_editor.page_editor_service import PageEditorService
from app.application.pipelines.events import PipelineListUpdated
from app.application.project.lifecycle_events import ProjectDirtyStateChanged
from app.application.page_editor.dto import ImageSelection


class PageEditorView(Protocol):
    def show_images(self, paths: list[str]) -> None: ...
    def clear_images(self) -> None: ...
    def set_pipeline_choices(self, choices: list[str]) -> None: ...
    def set_pipeline_value(self, value: Optional[str]) -> None: ...
    def set_view_mode(self, mode: str) -> None: ...
    def set_actions_enabled(self, *, has_active_unit: bool, has_selection: bool) -> None: ...
    def show_error(self, message: str) -> None: ...


class PageEditorPresenter:
    def __init__(self, service: PageEditorService, doc_unit_events, pipeline_events) -> None:
        self._service = service
        self._doc_unit_events = doc_unit_events
        self._pipeline_events = pipeline_events
        self._view: Optional[PageEditorView] = None
        self._controller = None
        self._active_unit_id: Optional[str] = None
        self._selection_ids: list[str] = []
        self._view_mode: str = "original"

        self._doc_unit_events.subscribe(ActiveDocUnitChanged, self._handle_active_unit_changed)
        self._doc_unit_events.subscribe(HierarchySelectionChanged, self._handle_selection_changed)
        self._doc_unit_events.subscribe(HierarchyUpdated, self._handle_hierarchy_updated)
        self._doc_unit_events.subscribe(HierarchyLoaded, self._handle_hierarchy_loaded)
        self._doc_unit_events.subscribe(ProjectDirtyStateChanged, self._handle_dirty_state)
        self._pipeline_events.subscribe(PipelineListUpdated, self._handle_pipeline_list_updated)

    def attach_view(self, view: PageEditorView, controller) -> None:
        self._view = view
        self._controller = controller
        self._controller.set_view(view)
        self._controller.update_selection(self._selection_ids)
        self._view.set_view_mode(self._view_mode)
        self._refresh_pipeline_choices()
        self._refresh_selection()

    def detach_view(self) -> None:
        self._view = None

    def refresh(self) -> None:
        self._refresh_pipeline_choices()
        self._refresh_selection()

    def set_view_mode(self, mode: str) -> None:
        normalized = "translated" if str(mode).lower().startswith("t") else "original"
        if normalized == self._view_mode:
            return
        self._view_mode = normalized
        if self._view:
            self._view.set_view_mode(self._view_mode)
        self._refresh_selection()

    def _handle_active_unit_changed(self, event: ActiveDocUnitChanged) -> None:
        self._active_unit_id = event.unit_id
        self._selection_ids = []
        if self._controller:
            self._controller.update_selection(self._selection_ids)
        self._refresh_selection()
        self._update_actions_state()

    def _handle_selection_changed(self, event: HierarchySelectionChanged) -> None:
        if self._active_unit_id and event.unit_id != self._active_unit_id:
            return
        self._selection_ids = list(dict.fromkeys(event.selected_node_ids))
        if self._controller:
            self._controller.update_selection(self._selection_ids)
        self._refresh_selection()

    def _handle_hierarchy_updated(self, event: HierarchyUpdated) -> None:
        if self._active_unit_id and event.unit_id != self._active_unit_id:
            return
        self._refresh_selection()

    def _handle_hierarchy_loaded(self, event: HierarchyLoaded) -> None:
        if self._active_unit_id and event.unit_id != self._active_unit_id:
            return
        self._refresh_selection()

    def _handle_pipeline_list_updated(self, _event) -> None:
        self._refresh_pipeline_choices()

    def _handle_dirty_state(self, _event) -> None:
        self._update_actions_state()

    def _refresh_pipeline_choices(self) -> None:
        if not self._view:
            return
        try:
            choices = self._service.list_pipelines()
            self._view.set_pipeline_choices(choices)
        except Exception as exc:
            self._view.show_error(str(exc))

    def _refresh_selection(self) -> None:
        if not self._view:
            return
        if not self._active_unit_id:
            self._view.clear_images()
            self._view.set_pipeline_value(None)
            self._update_actions_state()
            return
        try:
            images = self._service.resolve_selection(self._selection_ids)
        except Exception as exc:
            self._view.show_error(str(exc))
            self._view.clear_images()
            self._view.set_pipeline_value(None)
            self._update_actions_state()
            return

        self._view.show_images(self._paths_for_view(images))
        self._view.set_pipeline_value(self._common_pipeline(images))
        self._update_actions_state(has_selection=bool(self._selection_ids))

    def _paths_for_view(self, images: Sequence[ImageSelection]) -> list[str]:
        prefer_translated = self._view_mode == "translated"
        paths: list[str] = []
        for img in images:
            candidate = None
            if prefer_translated and img.translated_path and img.translated_path.exists():
                candidate = img.translated_path
            elif img.path and img.path.exists():
                candidate = img.path
            if candidate:
                paths.append(str(candidate))
        return paths

    def _common_pipeline(self, images: Sequence[ImageSelection]) -> Optional[str]:
        pipeline_ids = {img.pipeline_id for img in images if img.pipeline_id}
        if len(pipeline_ids) == 1:
            return pipeline_ids.pop()
        return None

    def _update_actions_state(self, *, has_selection: Optional[bool] = None) -> None:
        if not self._view:
            return
        selection_state = has_selection if has_selection is not None else bool(self._selection_ids)
        self._view.set_actions_enabled(
            has_active_unit=bool(self._active_unit_id),
            has_selection=selection_state,
        )
