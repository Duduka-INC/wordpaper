from dataclasses import dataclass
from enum import StrEnum


class FontWeight(StrEnum):
    REGULAR = "regular"
    MEDIUM = "medium"
    SEMIBOLD = "semibold"
    BOLD = "bold"


class FontStyle(StrEnum):
    NORMAL = "normal"
    ITALIC = "italic"


@dataclass(frozen=True)
class Font:
    font_id: str
    size_ratio: float
    weight: FontWeight = FontWeight.REGULAR
    style: FontStyle = FontStyle.NORMAL

    def __post_init__(self):
        if not self.font_id.strip():
            raise ValueError("font_id must not be empty")
        if not 0 < self.size_ratio < 1:
            raise ValueError("size_ratio must be between 0 and 1")
