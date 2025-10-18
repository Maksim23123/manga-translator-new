from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateProjectRequest:
    project_name: str


@dataclass(frozen=True, slots=True)
class SaveProjectRequest:
    path: str


@dataclass(frozen=True, slots=True)
class SaveProjectResponse:
    access_path: str


@dataclass(frozen=True, slots=True)
class LoadProjectRequest:
    path: str
