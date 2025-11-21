import logging
from pathlib import Path
from typing import Callable, Optional, Sequence

from app.application.doc_units.use_cases.finalize_doc_unit_assets import (
    FinalizeDocUnitAssets,
)
from app.application.project.use_cases.create_project import CreateProject
from app.application.project.use_cases.save_project import SaveProject
from app.application.project.use_cases.load_project import LoadProject
from app.application.project.dto import (
    CreateProjectRequest,
    SaveProjectRequest,
    LoadProjectRequest,
)
from app.application.project.errors import ProjectSaveLocationUndefinedError
from app.application.project.ports import ProjectSettingsStore
from app.application.project.lifecycle_events import (
    ProjectDirtyStateChanged,
    ProjectLifecycleEventBus,
)
from app.interface_adapters.project.util.fs_names import safe_folder_name

from ..presenters.main_window_presenter import MainWindowPresenter

log = logging.getLogger(__name__)


class MainWindowController:
    def __init__(
        self,
        presenter: MainWindowPresenter,
        create_project_use_case: CreateProject,
        save_project_use_case: SaveProject,
        load_project_use_case: LoadProject,
        project_settings_store: ProjectSettingsStore,
        lifecycle_event_bus: ProjectLifecycleEventBus,
        finalize_doc_unit_assets: FinalizeDocUnitAssets | None = None,
        finalize_pipeline_assets: Optional[Callable[[], None]] = None,
        project_ready_callbacks: Optional[Sequence[Callable[[], None]]] = None,
    ) -> None:
        self._presenter = presenter
        self._create_project_use_case = create_project_use_case
        self._save_project_use_case = save_project_use_case
        self._load_project_use_case = load_project_use_case
        self._project_settings_store = project_settings_store
        self._project_ready_callbacks = list(project_ready_callbacks or [])
        self._finalize_doc_unit_assets = finalize_doc_unit_assets
        self._finalize_pipeline_assets = finalize_pipeline_assets
        self._lifecycle_event_bus = lifecycle_event_bus

    def on_new_project_triggered(self) -> None:
        if project_name := self._presenter.request_project_name():
            req = CreateProjectRequest(project_name)
            self._create_project_use_case.execute(req)
            self._presenter.refresh_window_title()
            self._notify_project_ready()
            self._publish_clean_state()
            log.info(f"Project created. Project name: {project_name}")

    def on_save_project_triggered(self) -> None:
        try:
            if self._attempt_save(None):
                return
        except ProjectSaveLocationUndefinedError:
            self._prompt_and_save()
            return

    def on_save_project_as_triggered(self) -> None:
        self._prompt_and_save()

    def on_load_project_triggered(self) -> None:
        if load_location := self._presenter.request_load_location_path():
            try:
                req = LoadProjectRequest(load_location)
                self._load_project_use_case.execute(req)
                self._presenter.refresh_window_title()
                self._notify_project_ready()
                self._publish_clean_state()
                log.info("Project loaded")
            except Exception as ex:
                log.error(ex)
        log.debug("Load project triggered")

    def load_last_project_if_available(self) -> None:
        if not (last_path := self._project_settings_store.get_last_project_path()):
            return

        try:
            req = LoadProjectRequest(last_path)
            self._load_project_use_case.execute(req)
            self._presenter.refresh_window_title()
            self._notify_project_ready()
            self._publish_clean_state()
            log.info("Last project loaded")
        except Exception as ex:
            log.error(ex)
            self._project_settings_store.clear_last_project_path()

    def _notify_project_ready(self) -> None:
        for callback in self._project_ready_callbacks:
            try:
                callback()
            except Exception as ex:
                log.exception("Project ready callback failed: %s", ex)

    def _attempt_save(self, save_path: Optional[str]) -> bool: # TODO probably need to redesign use-cases for project saving. So they process all the cases
        try:
            project_slot = getattr(self._save_project_use_case, "project_slot", None)
            project_data = project_slot.get_data() if project_slot else None

            target_path = save_path or (project_data.metadata.get("project_meta_path") if project_data else None)
            if not target_path:
                raise ProjectSaveLocationUndefinedError("Project save location is undefined.")

            self._ensure_project_root_path(target_path)
            project_root_path = project_data.metadata.get("project_root_path") if project_data else None
            if not project_root_path:
                raise ProjectSaveLocationUndefinedError("Project root path is undefined.")

            if self._finalize_pipeline_assets:
                try:
                    self._finalize_pipeline_assets()
                except Exception as ex:
                    log.error("Pipeline asset finalization failed: %s", ex)

            if self._finalize_doc_unit_assets:
                self._finalize_doc_unit_assets.execute()

            req = SaveProjectRequest(save_path)
            response = self._save_project_use_case.execute(req)
            log.info(f"Project saved to: {response.access_path}")
            self._publish_clean_state()
            return True
        except ProjectSaveLocationUndefinedError:
            raise
        except Exception as ex:
            log.error(ex)
            return False

    def _prompt_and_save(self) -> None:
        if save_location := self._presenter.request_save_as_location_path():
            try:
                self._attempt_save(save_location)
            except ProjectSaveLocationUndefinedError:
                log.error("Save location remained undefined after prompting the user.")

    def _publish_clean_state(self) -> None:
        try:
            self._lifecycle_event_bus.publish(ProjectDirtyStateChanged(False))
        except Exception as ex:
            log.exception("Failed to publish clean state: %s", ex)

    def _ensure_project_root_path(self, save_path: str) -> None:
        """
        Populate project_root_path before finalizing assets so the media store
        knows where to write files on first save.
        """
        project_slot = getattr(self._save_project_use_case, "project_slot", None)
        if not project_slot:
            return

        project_data = project_slot.get_data()
        if not project_data:
            return
        if project_data.metadata.get("project_root_path"):
            return

        root_path = self._derive_project_root_path(save_path, project_data.name.value)
        project_data.metadata["project_root_path"] = root_path
        project_slot.set_data(project_data)

    def _derive_project_root_path(self, save_path: str, project_name: str) -> str:
        repository = getattr(self._save_project_use_case, "project_repository", None)
        base_path = Path(save_path)

        if repository and hasattr(repository, "resolve_meta"):
            meta_path = repository.resolve_meta(str(base_path))
            if meta_path:
                return str(meta_path.parent)

        project_dir_name = safe_folder_name(project_name)
        return str(base_path.joinpath(project_dir_name))
