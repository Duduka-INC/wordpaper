import unittest

from wordpaper_core.domain.anchor_position import AnchorPosition
from wordpaper_core.domain.text_layout import EdgeInsets, ResponsiveMargins, TextLayout
from wordpaper_core.rendering.pillow.text_placement import resolve_text_placement


class TextPlacementTests(unittest.TestCase):
    def setUp(self) -> None:
        margins = ResponsiveMargins(
            landscape=EdgeInsets(0.05, 0.05, 0.05, 0.05),
            portrait=EdgeInsets(0.05, 0.05, 0.05, 0.05),
        )
        self.layouts = {
            position: TextLayout(position=position, margins=margins)
            for position in AnchorPosition
        }

    def test_bottom_positions_have_even_horizontal_steps(self) -> None:
        positions = (
            AnchorPosition.BOTTOM_LEFT,
            AnchorPosition.BOTTOM_LEFT_MIDDLE,
            AnchorPosition.BOTTOM_CENTER,
            AnchorPosition.BOTTOM_RIGHT_MIDDLE,
            AnchorPosition.BOTTOM_RIGHT,
        )

        origins = [
            resolve_text_placement(
                self.layouts[position],
                width=1000,
                height=600,
                block_size=(470, 160),
            ).x
            for position in positions
        ]
        steps = [right - left for left, right in zip(origins, origins[1:])]

        self.assertLessEqual(max(steps) - min(steps), 1)
        self.assertEqual(origins[0], 50)
        self.assertEqual(origins[-1] + 470, 950)

    def test_side_positions_have_even_vertical_steps(self) -> None:
        positions = (
            AnchorPosition.TOP_LEFT,
            AnchorPosition.LEFT_TOP_MIDDLE,
            AnchorPosition.LEFT_CENTER,
            AnchorPosition.LEFT_BOTTOM_MIDDLE,
            AnchorPosition.BOTTOM_LEFT,
        )

        origins = [
            resolve_text_placement(
                self.layouts[position],
                width=1000,
                height=600,
                block_size=(470, 160),
            ).y
            for position in positions
        ]
        steps = [bottom - top for top, bottom in zip(origins, origins[1:])]

        self.assertLessEqual(max(steps) - min(steps), 1)
        self.assertEqual(origins[0], 30)
        self.assertEqual(origins[-1] + 160, 570)


if __name__ == "__main__":
    unittest.main()
