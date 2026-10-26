from dataclasses import dataclass
from enum import StrEnum

from wordpaper_core.domain.aspect_ratio import AspectRatio


@dataclass(frozen=True)
class Resolution:
    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Resolution values must be positive")


class ResolutionPreset(StrEnum):
    FULL_HD = "1080p"
    QHD_2K = "2k"
    UHD_4K = "4k"
    UHD_8K = "8k"

    @property
    def landscape_resolution(self) -> Resolution:
        dimensions = {
            ResolutionPreset.FULL_HD: Resolution(1920, 1080),
            ResolutionPreset.QHD_2K: Resolution(2560, 1440),
            ResolutionPreset.UHD_4K: Resolution(3840, 2160),
            ResolutionPreset.UHD_8K: Resolution(7680, 4320),
        }
        return dimensions[self]

    def resolve(self, aspect_ratio: AspectRatio) -> Resolution:
        reference = self.landscape_resolution

        if aspect_ratio.width >= aspect_ratio.height:
            width = reference.width
            height = round(width * aspect_ratio.height / aspect_ratio.width)
        else:
            height = reference.width
            width = round(height * aspect_ratio.width / aspect_ratio.height)

        return Resolution(width=width, height=height)
