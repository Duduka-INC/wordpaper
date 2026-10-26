from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    database_url: str
    storage_root: Path
    frontend_origin: str
    cookie_secure: bool


def load_settings() -> Settings:
    data_root = PROJECT_ROOT / ".data"
    database_url = os.getenv(
        "WORDPAPER_DATABASE_URL",
        f"sqlite:///{(data_root / 'wordpaper.db').as_posix()}",
    )
    storage_root = Path(
        os.getenv("WORDPAPER_STORAGE_ROOT", str(data_root / "storage"))
    ).resolve()
    return Settings(
        database_url=database_url,
        storage_root=storage_root,
        frontend_origin=os.getenv(
            "WORDPAPER_FRONTEND_ORIGIN",
            "http://localhost:5173",
        ),
        cookie_secure=os.getenv("WORDPAPER_COOKIE_SECURE", "false").lower()
        == "true",
    )


settings = load_settings()
