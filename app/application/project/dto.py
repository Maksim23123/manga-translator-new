from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateProjectRequest: project_name: str