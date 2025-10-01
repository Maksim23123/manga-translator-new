from typing import Protocol, Optional



class MainWindowView(Protocol):
    
    def prompt_project_name(self) -> Optional[str]: ...
    
    
    def prompt_location_for_new_project(self) -> Optional[str]: ...