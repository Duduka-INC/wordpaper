from dataclasses import dataclass


@dataclass(frozen=True)
class AssetRef:
    asset_id: str

    def __post_init__(self):
        if not self.asset_id.strip():
            raise ValueError("asset_id must not be empty")
