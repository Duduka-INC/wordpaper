from dataclasses import dataclass


@dataclass(frozen=True)
class RenderSize:
    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Render width and height must be positive")
