from __future__ import annotations

from typing import Optional, Sequence

from app.application.page_editor.page_editor_service import PageEditorService
from app.application.page_editor.dto import TranslationSummary
from app.interface_adapters.page_editor.page_editor_presenter import PageEditorView


class PageEditorController:
    def __init__(self, service: PageEditorService) -> None:
        self._service = service
        self._view: Optional[PageEditorView] = None
        self._selection_ids: list[str] = []

    def set_view(self, view: PageEditorView) -> None:
        self._view = view

    def update_selection(self, selection_ids: Sequence[str]) -> None:
        self._selection_ids = list(dict.fromkeys(selection_ids))

    def apply_pipeline(self, pipeline_id: str) -> None:
        if not self._selection_ids:
            self._show_error("Select at least one image or folder to assign a pipeline.")
            return
        try:
            self._service.apply_pipeline(self._selection_ids, pipeline_id)
        except Exception as exc:
            self._show_error(str(exc))

    def translate_all(self) -> None:
        try:
            summary = self._service.translate_all()
            self._report_translation_result(summary)
        except Exception as exc:
            self._show_error(str(exc))

    def translate_dirty(self) -> None:
        try:
            summary = self._service.translate_dirty()
            self._report_translation_result(summary)
        except Exception as exc:
            self._show_error(str(exc))

    def translate_selected(self) -> None:
        if not self._selection_ids:
            self._show_error("Select at least one image or folder to translate.")
            return
        try:
            summary = self._service.translate_selected(self._selection_ids)
            self._report_translation_result(summary)
        except Exception as exc:
            self._show_error(str(exc))

    def _report_translation_result(self, summary: TranslationSummary) -> None:
        if summary.failures and self._view:
            failures = "; ".join(summary.failures)
            self._view.show_error(f"Translation finished with errors: {failures}")

    def _show_error(self, message: str) -> None:
        if self._view:
            self._view.show_error(message)
