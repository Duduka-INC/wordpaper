from PIL import Image

from src.domain.wallpaper import Wallpaper


class WallpaperRender:
    def __init__(self, wallpaper: Wallpaper):
        self.wallpaper = wallpaper

    def create(self) -> Image.Image:
        return Image.new("RGB", (self.wallpaper.width, self.wallpaper.height))