from dataclasses import dataclass
from enum import StrEnum

from wordpaper_core.domain.resolution_preset import ResolutionPreset
from wordpaper_core.domain.wallpaper import Wallpaper


class ExportFormat(StrEnum):
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"


@dataclass(frozen=True)
class ExportRequest:
    wallpaper: Wallpaper
    export_format: ExportFormat
    output_path: str
    width: int
    height: int

    @classmethod
    def from_preset(
        cls,
        wallpaper: Wallpaper,
        export_format: ExportFormat,
        output_path: str,
        resolution_preset: ResolutionPreset,
    ):
        resolution = resolution_preset.resolve(wallpaper.aspect_ratio)
        return cls(
            wallpaper=wallpaper,
            export_format=export_format,
            output_path=output_path,
            width=resolution.width,
            height=resolution.height,
        )
