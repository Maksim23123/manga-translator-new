from typing import Optional

from app.application.doc_units.dto import (
    CreateDocUnitRequest,
    DeleteDocUnitRequest,
    ImportAssetRequest,
    RenameDocUnitRequest,
    SetActiveDocUnitRequest,
)
from app.application.doc_units.use_cases.create_doc_unit import CreateDocUnit
from app.application.doc_units.use_cases.delete_doc_unit import DeleteDocUnit
from app.application.doc_units.use_cases.import_doc_unit_asset import (
    ImportDocUnitAsset,
)
from app.application.doc_units.use_cases.rename_doc_unit import RenameDocUnit
from app.application.doc_units.use_cases.set_active_doc_unit import (
    SetActiveDocUnit,
)


class DocUnitController:
    def __init__(
        self,
        create_use_case: CreateDocUnit,
        rename_use_case: RenameDocUnit,
        delete_use_case: DeleteDocUnit,
        set_active_use_case: SetActiveDocUnit,
        import_asset_use_case: ImportDocUnitAsset,
    ) -> None:
        self._create_use_case = create_use_case
        self._rename_use_case = rename_use_case
        self._delete_use_case = delete_use_case
        self._set_active_use_case = set_active_use_case
        self._import_asset_use_case = import_asset_use_case

    def create_doc_unit(self, name: str):
        return self._create_use_case.execute(CreateDocUnitRequest(name=name))

    def rename_doc_unit(self, unit_id: str, new_name: str):
        return self._rename_use_case.execute(
            RenameDocUnitRequest(unit_id=unit_id, new_name=new_name)
        )

    def delete_doc_unit(self, unit_id: str) -> None:
        self._delete_use_case.execute(DeleteDocUnitRequest(unit_id=unit_id))

    def set_active_doc_unit(self, unit_id: Optional[str]) -> None:
        self._set_active_use_case.execute(SetActiveDocUnitRequest(unit_id=unit_id))

    def import_asset(self, unit_id: str, source_path: str):
        return self._import_asset_use_case.execute(
            ImportAssetRequest(unit_id=unit_id, source_path=source_path)
        )
