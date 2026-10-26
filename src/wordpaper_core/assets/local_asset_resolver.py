from collections.abc import Mapping
from pathlib import Path

from wordpaper_core.domain.asset_ref import AssetRef


class LocalAssetResolver:
    def __init__(
        self,
        root_directory: Path,
        asset_paths: Mapping[str, str],
    ):
        self._root_directory = root_directory.resolve()
        self._asset_paths = dict(asset_paths)

    def resolve(self, asset: AssetRef) -> Path:
        relative_path = self._asset_paths.get(asset.asset_id)
        if relative_path is None:
            raise KeyError(f"Unknown asset: {asset.asset_id}")

        resolved_path = (self._root_directory / relative_path).resolve()

        try:
            resolved_path.relative_to(self._root_directory)
        except ValueError as error:
            raise ValueError(
                f"Asset points outside the asset directory: {asset.asset_id}"
            ) from error

        if not resolved_path.is_file():
            raise FileNotFoundError(
                f"Asset file does not exist: {resolved_path}"
            )

        return resolved_path
