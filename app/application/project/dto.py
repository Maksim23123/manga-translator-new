from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateProjectRequest: project_name: str


@dataclass(frozen=True, slots=True)
class SaveProjectRequest: uri: str
@dataclass(frozen=True, slots=True)
class SaveProjectResponse: access_uri: str 


@dataclass(frozen=True, slots=True)
class LoadProjectRequest: uri: str
