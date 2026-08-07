from dataclasses import dataclass
from src.domain.aspect_ratio import AspectRatio
from src.domain.background import Background
from src.domain.text import Text


@dataclass(frozen=True)
class Wallpaper:
    text: Text
    background: Background
    aspect_ratio: AspectRatio
