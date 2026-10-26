from pathlib import Path


class LocalObjectStorage:
    def __init__(self, root: Path):
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes) -> Path:
        path = (self._root / key).resolve()
        try:
            path.relative_to(self._root)
        except ValueError as error:
            raise ValueError("Storage key escapes the storage root") from error
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def resolve(self, key: str) -> Path:
        path = (self._root / key).resolve()
        try:
            path.relative_to(self._root)
        except ValueError as error:
            raise ValueError("Storage key escapes the storage root") from error
        if not path.is_file():
            raise FileNotFoundError(key)
        return path

    @staticmethod
    def public_url(key: str) -> str:
        normalized_key = key.replace("\\", "/")
        return f"/media/{normalized_key}"
