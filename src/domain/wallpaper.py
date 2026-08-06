from dataclasses import dataclass
from src.domain.background import Background
from src.domain.text import Text


@dataclass(frozen=True)
class Wallpaper:
    text: Text
    background: Background
    width: int = 3840
    height: int = 2160
