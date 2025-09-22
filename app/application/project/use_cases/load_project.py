from ..ports import CurrentProjectStore, ProjectRepository
from ..dto import LoadProjectRequest
from ..errors import InvalidProjectDataError


class LoadProject:
    def __init__(self, project_slot: CurrentProjectStore, project_repository: ProjectRepository):
        self.project_slot, self.project_repository = project_slot, project_repository
    
    
    def execute(self, req: LoadProjectRequest):
        project_data = self.project_repository.load(req.uri)
        self.project_slot.set_data(project_data)