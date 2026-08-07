from abc import ABC, abstractmethod
from src.domain.wallpaper import Wallpaper
from src.rendering.render_size import RenderSize
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
