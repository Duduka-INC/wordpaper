from enum import StrEnum


class ImageFit(StrEnum):
    COVER = "cover"
    CONTAIN = "contain"
    STRETCH = "stretch"
    TILE = "tile"
