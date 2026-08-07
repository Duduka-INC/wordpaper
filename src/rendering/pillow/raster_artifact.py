from dataclasses import dataclass


@dataclass(frozen=True)
class RasterArtifact:
    width: int
    height: int
    pixels: bytes