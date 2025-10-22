from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    project_name: str


@dataclass(frozen=True, slots=True)
class SaveProjectRequest:
    path: Optional[str] = None


@dataclass(frozen=True, slots=True)
class SaveProjectResponse:
    access_path: str


@dataclass(frozen=True, slots=True)
class LoadProjectRequest:
    path: str
