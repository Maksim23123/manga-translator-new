from typing import Protocol, Optional
from domain.project.value_objects import ProjectData



class IdGenerator(Protocol):
    def generate(self) -> str: ...
    

class CurrentProjectStore(Protocol):
    def get_data(self) -> Optional[ProjectData]: ...
    def set_data(self, project_data: Optional[ProjectData]) -> None: ...


class ProjectRepository(Protocol):
    def load(self, uri: str) -> ProjectData: ...
    def save(self, uri:str, project_data: ProjectData) -> str: ...