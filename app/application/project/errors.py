from typing import Optional



class ProjectIdMismatchError(Exception):
    """Raised when a save/update targets a file with a different project id."""


class ProjectDoesntExistError(Exception):
    """Raised when trying to load project that doesn't exist."""
    def __init__(self, path: str):
        super().__init__(f"Project under the path \"{path}\" doesn't exist.")


class ProjectOverwriteError(Exception):
    """Raised when trying to save on project on top of another."""
    
    DEFAULT_MSG = "Trying to save on project on top of another."
    
    def __init__(self, msg: Optional[str] = None) -> None:
        final_message = msg or self.DEFAULT_MSG
        super().__init__(final_message)


class InvalidPathError(Exception):
    """Raised when invalid path was passed."""
    

class InvalidProjectDataError(Exception):
    """Raised when received project data is invalid."""