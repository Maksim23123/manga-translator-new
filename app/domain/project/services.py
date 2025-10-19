from .value_objects import ProjectData, ProjectID, ProjectName


def new_project(id: str, name: str) -> ProjectData:
    return ProjectData(
        project_id=ProjectID(id),
        name=ProjectName(name),
        doc_units={},
        last_active_doc_unit_id=None,
        metadata={},
    )
