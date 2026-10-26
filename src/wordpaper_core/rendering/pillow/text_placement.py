from dataclasses import dataclass

from wordpaper_core.domain.anchor_position import AnchorPosition
from wordpaper_core.domain.text_layout import TextLayout


@dataclass(frozen=True)
class ResolvedTextPlacement:
    x: int
    y: int


_PLACEMENTS: dict[AnchorPosition, tuple[float, float]] = {
    AnchorPosition.TOP_LEFT: (0.0, 0.0),
    AnchorPosition.TOP_LEFT_MIDDLE: (0.25, 0.0),
    AnchorPosition.TOP_CENTER: (0.5, 0.0),
    AnchorPosition.TOP_RIGHT_MIDDLE: (0.75, 0.0),
    AnchorPosition.TOP_RIGHT: (1.0, 0.0),
    AnchorPosition.LEFT_TOP_MIDDLE: (0.0, 0.25),
    AnchorPosition.LEFT_CENTER: (0.0, 0.5),
    AnchorPosition.LEFT_BOTTOM_MIDDLE: (0.0, 0.75),
    AnchorPosition.CENTER: (0.5, 0.5),
    AnchorPosition.RIGHT_TOP_MIDDLE: (1.0, 0.25),
    AnchorPosition.RIGHT_CENTER: (1.0, 0.5),
    AnchorPosition.RIGHT_BOTTOM_MIDDLE: (1.0, 0.75),
    AnchorPosition.BOTTOM_LEFT: (0.0, 1.0),
    AnchorPosition.BOTTOM_LEFT_MIDDLE: (0.25, 1.0),
    AnchorPosition.BOTTOM_CENTER: (0.5, 1.0),
    AnchorPosition.BOTTOM_RIGHT_MIDDLE: (0.75, 1.0),
    AnchorPosition.BOTTOM_RIGHT: (1.0, 1.0),
}


def resolve_text_placement(
    layout: TextLayout,
    width: int,
    height: int,
    block_size: tuple[int, int],
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

    block_width, block_height = block_size
    if block_width < 0 or block_height < 0:
        raise ValueError("Block width and height must not be negative")

    horizontal_position, vertical_position = _PLACEMENTS[layout.position]
    horizontal_travel = max(0.0, right - left - block_width)
    vertical_travel = max(0.0, bottom - top - block_height)

    x = left + horizontal_travel * horizontal_position
    y = top + vertical_travel * vertical_position

    return ResolvedTextPlacement(
        x=round(x),
        y=round(y),
    )
