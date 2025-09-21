from ..ports import ProjectRepository, CurrentProjectStore, IdGenerator
from ..dto import CreateProjectRequest
from domain.project.value_objects import ProjectID, ProjectData, ProjectName



class CreateProject:
    def __init__(self, project_slot: CurrentProjectStore, ids: IdGenerator):
        self.project_slot, self.ids = project_slot, ids
    
    
    def execute(self, req: CreateProjectRequest):
        project_id = ProjectID(self.ids.generate())
        project_name = ProjectName(req.project_name)
        project_data = ProjectData(
            project_id,
            project_name
            )
        self.project_slot.set_data(project_data)
        
        
        