from dataclasses import dataclass

@dataclass(frozen=True)
class Font:
    name: str
    size: int
    type: str
    color: tuple[int, int, int]