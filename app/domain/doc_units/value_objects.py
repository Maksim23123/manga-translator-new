from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DocUnitId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("DocUnitId must not be empty.")


@dataclass(frozen=True, slots=True)
class DocUnitName:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("DocUnitName must not be empty.")


@dataclass(frozen=True, slots=True)
class AssetId:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("AssetId must not be empty.")
