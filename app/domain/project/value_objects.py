from dataclasses import dataclass



@dataclass(frozen=True)
class ProjectName:
    value: str
    def __post_init__(self):
        if not self.value.strip():
            raise ValueError('Project name must not be empty')


@dataclass(frozen=True)
class ProjectID:
    value: str
    

@dataclass(frozen=True, slots=True)
class ProjectData:
    project_id: ProjectID
    name: ProjectName
    

