from dataclasses import dataclass

from wordpaper_core.domain.anchor_position import AnchorPosition


@dataclass(frozen=True)
class EdgeInsets:
    top: float
    right: float
    bottom: float
    left: float

    def __post_init__(self):
        values = (self.top, self.right, self.bottom, self.left)

        if any(not 0 <= value < 1 for value in values):
            raise ValueError("Every inset must be between 0 and 1")

        if self.left + self.right >= 1:
            raise ValueError("Left and right insets must leave usable width")

        if self.top + self.bottom >= 1:
            raise ValueError("Top and bottom insets must leave usable height")


@dataclass(frozen=True)
class ResponsiveMargins:
    landscape: EdgeInsets
    portrait: EdgeInsets


@dataclass(frozen=True)
class TextLayout:
    position: AnchorPosition
    margins: ResponsiveMargins
