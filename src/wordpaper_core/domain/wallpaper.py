from dataclasses import dataclass
from wordpaper_core.domain.aspect_ratio import AspectRatio
from wordpaper_core.domain.background import Background
from wordpaper_core.domain.text import Text


@dataclass(frozen=True)
class Wallpaper:
    text: Text
    background: Background
    aspect_ratio: AspectRatio
