from typing import Protocol, Optional



class MainWindowView(Protocol):
    
    def prompt_project_name(self) -> Optional[str]: ...