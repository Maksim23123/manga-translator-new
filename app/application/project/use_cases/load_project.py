from ..ports import CurrentProjectStore, ProjectRepository
from ..dto import LoadProjectRequest
from ..errors import InvalidProjectDataError


class LoadProject:
    def __init__(self, project_slot: CurrentProjectStore, project_repository: ProjectRepository):
        self.project_slot, self.project_repository = project_slot, project_repository
    
    
    def execute(self, req: LoadProjectRequest) -> str:
        if project_data := self.project_slot.get_data():
            return self.project_repository.save(req.uri, project_data)
        else:
            raise InvalidProjectDataError("Project slot is empty")