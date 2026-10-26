from abc import ABC, abstractmethod
from wordpaper_core.domain.wallpaper import Wallpaper
from wordpaper_core.rendering.render_size import RenderSize
from typing import Generic, TypeVar

TArtifact = TypeVar("TArtifact")

class Renderer(ABC, Generic[TArtifact]):
    @abstractmethod
    def render(
        self,
        wallpaper: Wallpaper,
        render_size: RenderSize,
    ) -> TArtifact:
        pass
