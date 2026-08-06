from dataclasses import dataclass
from enum import StrEnum

from src.domain.wallpaper import Wallpaper


@dataclass(frozen=True)
class ExportRequest:
    wallpaper: Wallpaper
    export_format: ExportFormat
    output_path: str
    width: int
    height: int


class ExportFormat(StrEnum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"