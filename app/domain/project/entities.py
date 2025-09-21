from dataclasses import dataclass
from .value_objects import ProjectData, ProjectID

@dataclass
class Project:
    id: ProjectID
    data: ProjectData