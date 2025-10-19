from ..ports import CurrentProjectStore, IdGenerator
from ..dto import CreateProjectRequest
from app.domain.project.services import new_project


class CreateProject:
    def __init__(self, project_slot: CurrentProjectStore, ids: IdGenerator):
        self.project_slot, self.ids = project_slot, ids

    def execute(self, req: CreateProjectRequest):
        project_data = new_project(self.ids.generate(), req.project_name)
        self.project_slot.set_data(project_data)
