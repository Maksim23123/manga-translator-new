from interface_adapters.project.repositories.fs_project_repository import FsProjectRepository
from domain.project.services import new_project


project_repo = FsProjectRepository()

base_path = "C:/Users/makss/My_projects/ABNS/Diploma/manga-translator-new/data/projects/MY PROJECT"

project_data = new_project("myid123", "MY PROJECT(name changed)")

project_repo.save(base_path, project_data)
# project_data = project_repo.load(base_path)

print(project_data)