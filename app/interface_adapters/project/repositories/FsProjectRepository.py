from pathlib import Path
from application.project.ports import ProjectRepository
from domain.project.value_objects import ProjectData
from typing import Optional
import json
from application.project.errors import ProjectIdMismatchError, ProjectDoesntExistError, ProjectOverwriteError

from ..mappers.project_data_mapper import to_dict, from_dict
from ..util.fs_names import safe_folder_name



class FsProjectRepository(ProjectRepository):
    
    PROJECT_META_FILE_NAME = "project.mtmeta"
    
    def __init__(self):
        self._default_project_dirs: list = [
            "temp",
            "docs_units",
            "pipelines"
        ]
    
    def load(self, uri: str) -> ProjectData: 
        path = Path(uri)
        
        if meta_path := self.resolve_meta(str(path)):
            return self._read_from_file(Path(meta_path))
        
        raise ProjectDoesntExistError(str(path))
            
    
    def _read_from_file(self, path: Path) -> ProjectData:
        project_data_dict = json.loads(path.read_text(encoding="utf-8"))
        return from_dict(project_data_dict)
        
        
    def save(self, uri: str, project_data: ProjectData) -> str: 
        path = Path(uri)
        if not isinstance(project_data, ProjectData):
            raise TypeError(f"Expected type of project_data is {ProjectData.__name__}. Got {type(project_data).__name__}")
        
        if meta_path := self.resolve_meta(str(path)):
            return self._atomic_write_json(Path(meta_path), project_data)
        
        project_dir_name = safe_folder_name(project_data.name.value)
        return self._create_project_files(path, project_dir_name, project_data)
    
    
    def _atomic_write_json(self, file_path: Path, project_data: ProjectData):
        if file_path.exists() and file_path.is_file():
            project_data_in_file = self._read_from_file(file_path)
            if project_data_in_file.project_id != project_data.project_id:
                raise ProjectIdMismatchError(f"Existing id {project_data_in_file.project_id} != incoming {project_data.project_id}")
        
        project_data_dict = to_dict(project_data)
        tmp = file_path.with_suffix(file_path.suffix + ".tmp")
        tmp.write_text(json.dumps(project_data_dict, ensure_ascii=False, indent=2),encoding="utf-8")
        tmp.replace(file_path)
        return str(file_path)
        
    
    def _create_project_files(self, path: Path, project_dir_name: str, project_data: ProjectData):
        
        project_folder_path = path.joinpath(project_dir_name)
        if self.resolve_meta(str(project_folder_path)):
            raise ProjectOverwriteError()
        
        for sub_dir in self._default_project_dirs:
            dir_path = path.joinpath(project_dir_name, sub_dir)
            dir_path.mkdir(parents=True, exist_ok=True)
        
        project_meta_file_path = project_folder_path.joinpath(self.PROJECT_META_FILE_NAME)
        self._atomic_write_json(project_meta_file_path, project_data)
        return str(project_meta_file_path)


    def resolve_meta(self, path_string: str) -> Optional[Path]:
        path = Path(path_string)
        if path.exists():
            if path.is_file():
                return path
            meta_path = path.joinpath(self.PROJECT_META_FILE_NAME)
            if meta_path.exists() and meta_path.is_file():
                return meta_path
        return None
    
