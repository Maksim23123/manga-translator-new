from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ProjectName:
    value: str

    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("Project name must not be empty")


@dataclass(frozen=True)
class ProjectID:
    value: str


@dataclass(slots=True)
class ProjectData:
    project_id: ProjectID
    name: ProjectName
    doc_units: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_active_doc_unit_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

