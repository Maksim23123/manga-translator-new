from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CreateDocUnitRequest:
    name: str


@dataclass(slots=True)
class RenameDocUnitRequest:
    unit_id: str
    new_name: str


@dataclass(slots=True)
class DeleteDocUnitRequest:
    unit_id: str


@dataclass(slots=True)
class SetActiveDocUnitRequest:
    unit_id: Optional[str]


@dataclass(slots=True)
class ImportAssetRequest:
    unit_id: str
    source_path: str
