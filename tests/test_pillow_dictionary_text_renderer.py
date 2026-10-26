import unittest

from wordpaper_core.domain.anchor_position import AnchorPosition
from wordpaper_core.domain.font import Font, FontWeight
from wordpaper_core.domain.operation_plan import OperationPipeline
from wordpaper_core.domain.text import Text
from wordpaper_core.domain.text_layout import (
    EdgeInsets,
    ResponsiveMargins,
    TextLayout,
)
from wordpaper_core.rendering.pillow.pillow_dictionary_text_renderer import (
    PillowDictionaryTextRenderer,
)
from wordpaper_core.rendering.pillow.pillow_font_resolver import PillowFontResolver


class PillowDictionaryTextRendererTests(unittest.TestCase):
    def test_renders_complete_dictionary_block_inside_canvas(self):
        margins = ResponsiveMargins(
            landscape=EdgeInsets(0.05, 0.05, 0.1, 0.05),
            portrait=EdgeInsets(0.05, 0.05, 0.05, 0.05),
        )
        text = Text(
            text="consistency",
            description="the ability to repeat a process with the same quality",
            font=Font("playfair_display", 0.06, FontWeight.BOLD),
            operation_pipeline=OperationPipeline([]),
            layout=TextLayout(AnchorPosition.BOTTOM_LEFT, margins),
            transcription="[kənˈsɪstənsi]",
            part_of_speech="noun",
            language="English",
            underline=True,
        )
        renderer = PillowDictionaryTextRenderer(
            PillowFontResolver.create_default()
        )

        mask = renderer.render_mask(text, (1920, 1080))

        self.assertEqual(mask.size, (1920, 1080))
        self.assertIsNotNone(mask.getbbox())
        left, top, right, bottom = mask.getbbox()
        self.assertGreaterEqual(left, 0)
        self.assertGreaterEqual(top, 0)
        self.assertLessEqual(right, mask.width)
        self.assertLessEqual(bottom, mask.height)

    def test_long_title_font_is_fitted_to_block_width(self):
        margins = ResponsiveMargins(
            landscape=EdgeInsets(0.05, 0.05, 0.1, 0.05),
            portrait=EdgeInsets(0.05, 0.05, 0.05, 0.05),
        )
        text = Text(
            text="hyperconsistency",
            description="a deliberately long title",
            font=Font("orbitron", 0.08, FontWeight.BOLD),
            operation_pipeline=OperationPipeline([]),
            layout=TextLayout(AnchorPosition.BOTTOM_LEFT, margins),
        )
        renderer = PillowDictionaryTextRenderer(
            PillowFontResolver.create_default()
        )

        fitted = renderer._resolve_title_font(text, 1920, 900)

        self.assertLessEqual(fitted.getlength(text.text), 900)


if __name__ == "__main__":
    unittest.main()
