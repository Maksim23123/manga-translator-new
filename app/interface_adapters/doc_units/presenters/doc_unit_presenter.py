from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    DocUnitEventBus,
    DocUnitListUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.use_cases.list_doc_units import ListDocUnits


@dataclass(slots=True)
class DocUnitViewModel:
    unit_id: str
    name: str
    created_at: Optional[str]


class DocUnitView(Protocol):
    def display_units(self, units: list[DocUnitViewModel]) -> None: ...
    def highlight_active(self, unit_id: Optional[str]) -> None: ...
    def show_dirty_state(self, is_dirty: bool) -> None: ...
    def show_error(self, message: str) -> None: ...


class DocUnitPresenter:
    def __init__(self, event_bus: DocUnitEventBus, list_use_case: ListDocUnits) -> None:
        self._event_bus = event_bus
        self._list_use_case = list_use_case
        self._view: Optional[DocUnitView] = None
        self._suppress_no_project_errors = True

        self._event_bus.subscribe(DocUnitListUpdated, self._handle_doc_units_updated)
        self._event_bus.subscribe(ActiveDocUnitChanged, self._handle_active_changed)
        self._event_bus.subscribe(ProjectDirtyStateChanged, self._handle_dirty_state)

    def attach_view(self, view: DocUnitView) -> None:
        self._view = view
        self._refresh_units()

    def detach_view(self) -> None:
        self._view = None

    def refresh(self) -> None:
        self._refresh_units()

    def _handle_doc_units_updated(self, event: DocUnitListUpdated) -> None:
        self._refresh_units()

    def _handle_active_changed(self, event: ActiveDocUnitChanged) -> None:
        if self._view:
            self._view.highlight_active(event.unit_id)

    def _handle_dirty_state(self, event: ProjectDirtyStateChanged) -> None:
        if self._view:
            self._view.show_dirty_state(event.is_dirty)

    def _refresh_units(self) -> None:
        if not self._view:
            return
        try:
            units = self._list_use_case.execute()
            view_models = [
                DocUnitViewModel(
                    unit_id=unit.unit_id.value,
                    name=unit.name.value,
                    created_at=unit.created_at,
                )
                for unit in units
            ]
            self._view.display_units(view_models)
        except RuntimeError as exc:
            if self._suppress_no_project_errors and str(exc) == "No project loaded.":
                return
            if self._view:
                self._view.show_error(str(exc))
        except Exception as exc:
            if self._view:
                self._view.show_error(str(exc))
