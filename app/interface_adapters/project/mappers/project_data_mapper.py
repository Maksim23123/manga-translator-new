from domain.project.services import new_project
from domain.project.value_objects import ProjectData

_SCHEMA_VERSION = 1

def to_dict(project_data: ProjectData) -> dict:
    return {
        "schema_version": _SCHEMA_VERSION,
        "project_id": project_data.project_id.value,
        "project_name": project_data.name.value 
    }
    

def from_dict(project_data_dict: dict) -> ProjectData:
    return new_project(
        id=project_data_dict["project_id"],
        name=project_data_dict["project_name"]
        )
