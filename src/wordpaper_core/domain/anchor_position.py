from enum import StrEnum


class AnchorPosition(StrEnum):
    TOP_LEFT = "top_left"
    TOP_LEFT_MIDDLE = "top_left_middle"
    TOP_CENTER = "top_center"
    TOP_RIGHT_MIDDLE = "top_right_middle"
    TOP_RIGHT = "top_right"

    LEFT_TOP_MIDDLE = "left_top_middle"
    LEFT_CENTER = "left_center"
    LEFT_BOTTOM_MIDDLE = "left_bottom_middle"

    CENTER = "center"

    RIGHT_TOP_MIDDLE = "right_top_middle"
    RIGHT_CENTER = "right_center"
    RIGHT_BOTTOM_MIDDLE = "right_bottom_middle"

    BOTTOM_LEFT = "bottom_left"
    BOTTOM_LEFT_MIDDLE = "bottom_left_middle"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT_MIDDLE = "bottom_right_middle"
    BOTTOM_RIGHT = "bottom_right"
