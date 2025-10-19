from typing import Any, Dict

from app.domain.project.value_objects import ProjectData, ProjectID, ProjectName

_SCHEMA_VERSION = 2


def to_dict(project_data: ProjectData) -> dict:
    return {
        "schema_version": _SCHEMA_VERSION,
        "project_id": project_data.project_id.value,
        "project_name": project_data.name.value,
        "doc_units": project_data.doc_units,
        "last_active_doc_unit_id": project_data.last_active_doc_unit_id,
        "metadata": project_data.metadata,
    }


def from_dict(project_data_dict: dict) -> ProjectData:
    doc_units: Dict[str, Dict[str, Any]] = project_data_dict.get("doc_units", {})
    last_active = project_data_dict.get("last_active_doc_unit_id")
    metadata = project_data_dict.get("metadata", {})

    return ProjectData(
        project_id=ProjectID(project_data_dict["project_id"]),
        name=ProjectName(project_data_dict["project_name"]),
        doc_units=doc_units,
        last_active_doc_unit_id=last_active,
        metadata=metadata,
    )
