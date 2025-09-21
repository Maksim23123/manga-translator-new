from .value_objects import ProjectData, ProjectID, ProjectName



def new_project(id: str, name: str) -> ProjectData:
    return ProjectData(ProjectID(id), ProjectName(name))
    