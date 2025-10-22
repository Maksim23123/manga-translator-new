from ..ports import CurrentProjectStore, ProjectRepository, ProjectSettingsStore
from ..dto import LoadProjectRequest


class LoadProject:
    def __init__(
        self,
        project_slot: CurrentProjectStore,
        project_repository: ProjectRepository,
        project_settings_store: ProjectSettingsStore,
    ):
        self.project_slot = project_slot
        self.project_repository = project_repository
        self.project_settings_store = project_settings_store


    def execute(self, req: LoadProjectRequest):
        project_data = self.project_repository.load(req.path)
        self.project_slot.set_data(project_data)
        meta_path = project_data.metadata.get("project_meta_path") or req.path
        if meta_path:
            self.project_settings_store.set_last_project_path(meta_path)
        else:
            self.project_settings_store.clear_last_project_path()
