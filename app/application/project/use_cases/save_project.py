from ..ports import CurrentProjectStore, ProjectRepository, ProjectSettingsStore
from ..dto import SaveProjectRequest, SaveProjectResponse
from ..errors import InvalidProjectDataError, ProjectSaveLocationUndefinedError


class SaveProject:
    def __init__(
        self,
        project_slot: CurrentProjectStore,
        project_repository: ProjectRepository,
        project_settings_store: ProjectSettingsStore,
    ):
        self.project_slot = project_slot
        self.project_repository = project_repository
        self.project_settings_store = project_settings_store


    def execute(self, req: SaveProjectRequest) -> SaveProjectResponse:
        if project_data := self.project_slot.get_data():
            save_path = req.path or project_data.metadata.get("project_meta_path")
            if not save_path:
                raise ProjectSaveLocationUndefinedError("Project save location is undefined.")

            access_path = self.project_repository.save(save_path, project_data)
            project_data.metadata["project_meta_path"] = access_path
            self.project_slot.set_data(project_data)
            self.project_settings_store.set_last_project_path(access_path)
            return SaveProjectResponse(access_path)

        raise InvalidProjectDataError("Project slot is empty")
