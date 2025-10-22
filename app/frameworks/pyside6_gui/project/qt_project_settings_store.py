from typing import Optional

from PySide6.QtCore import QSettings

from app.application.project.ports import ProjectSettingsStore


class QtProjectSettingsStore(ProjectSettingsStore):
    LAST_PROJECT_KEY = "project/last_meta_path"

    def __init__(self, organization: str = "MangaTranslator", application: str = "MangaTranslator"):
        self._settings = QSettings(organization, application)

    def get_last_project_path(self) -> Optional[str]:
        value = self._settings.value(self.LAST_PROJECT_KEY, type=str)
        return value or None

    def set_last_project_path(self, path: str) -> None:
        self._settings.setValue(self.LAST_PROJECT_KEY, path)

    def clear_last_project_path(self) -> None:
        self._settings.remove(self.LAST_PROJECT_KEY)
