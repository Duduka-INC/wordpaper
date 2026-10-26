from dataclasses import dataclass

from wordpaper_core.domain.anchor_position import AnchorPosition
from wordpaper_core.domain.text_layout import TextLayout


@dataclass(frozen=True)
class ResolvedTextPlacement:
    x: int
    y: int
    anchor: str


_PLACEMENTS: dict[AnchorPosition, tuple[float, float, str]] = {
    AnchorPosition.TOP_LEFT: (0.0, 0.0, "lt"),
    AnchorPosition.TOP_LEFT_MIDDLE: (0.25, 0.0, "mt"),
    AnchorPosition.TOP_CENTER: (0.5, 0.0, "mt"),
    AnchorPosition.TOP_RIGHT_MIDDLE: (0.75, 0.0, "mt"),
    AnchorPosition.TOP_RIGHT: (1.0, 0.0, "rt"),
    AnchorPosition.LEFT_TOP_MIDDLE: (0.0, 0.25, "lm"),
    AnchorPosition.LEFT_CENTER: (0.0, 0.5, "lm"),
    AnchorPosition.LEFT_BOTTOM_MIDDLE: (0.0, 0.75, "lm"),
    AnchorPosition.CENTER: (0.5, 0.5, "mm"),
    AnchorPosition.RIGHT_TOP_MIDDLE: (1.0, 0.25, "rm"),
    AnchorPosition.RIGHT_CENTER: (1.0, 0.5, "rm"),
    AnchorPosition.RIGHT_BOTTOM_MIDDLE: (1.0, 0.75, "rm"),
    AnchorPosition.BOTTOM_LEFT: (0.0, 1.0, "lb"),
    AnchorPosition.BOTTOM_LEFT_MIDDLE: (0.25, 1.0, "mb"),
    AnchorPosition.BOTTOM_CENTER: (0.5, 1.0, "mb"),
    AnchorPosition.BOTTOM_RIGHT_MIDDLE: (0.75, 1.0, "mb"),
    AnchorPosition.BOTTOM_RIGHT: (1.0, 1.0, "rb"),
}


def resolve_text_placement(
    layout: TextLayout,
    width: int,
    height: int,
) -> ResolvedTextPlacement:
    if width <= 0 or height <= 0:
        raise ValueError("Canvas width and height must be positive")

    margins = (
        layout.margins.portrait
        if width < height
        else layout.margins.landscape
    )

    left = width * margins.left
    right = width * (1 - margins.right)
    top = height * margins.top
    bottom = height * (1 - margins.bottom)

    horizontal_position, vertical_position, anchor = _PLACEMENTS[layout.position]

    x = left + (right - left) * horizontal_position
    y = top + (bottom - top) * vertical_position

    return ResolvedTextPlacement(
        x=round(x),
        y=round(y),
        anchor=anchor,
    )
