from app.application.doc_units.ports import DocUnitRepository


class ListDocUnits:
    def __init__(self, repository: DocUnitRepository) -> None:
        self._repository = repository

    def execute(self):
        return self._repository.list_units()
