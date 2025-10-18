from ..ports import CurrentProjectStore, ProjectRepository
from ..dto import SaveProjectRequest, SaveProjectResponse
from ..errors import InvalidProjectDataError


class SaveProject:
    def __init__(self, project_slot: CurrentProjectStore, project_repository: ProjectRepository):
        self.project_slot, self.project_repository = project_slot, project_repository


    def execute(self, req: SaveProjectRequest) -> SaveProjectResponse:
        if project_data := self.project_slot.get_data():
            access_path = self.project_repository.save(req.path, project_data)
            return SaveProjectResponse(access_path)
        else:
            raise InvalidProjectDataError("Project slot is empty")
