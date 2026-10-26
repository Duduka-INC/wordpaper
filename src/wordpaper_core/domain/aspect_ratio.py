from dataclasses import dataclass
from math import gcd


@dataclass(frozen=True)
class AspectRatio:
    width: int
    height: int

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Aspect ratio values must be positive")

        divisor = gcd(self.width, self.height)
        object.__setattr__(self, "width", self.width // divisor)
        object.__setattr__(self, "height", self.height // divisor)
