import unittest

import wordpaper_core

from wordpaper_core.assets.default_asset_catalog import (
    DEFAULT_ASSET_PATHS,
    create_default_asset_resolver,
)
from wordpaper_core.domain.asset_ref import AssetRef
from wordpaper_core.domain.font import Font, FontWeight
from wordpaper_core.rendering.pillow.pillow_font_resolver import PillowFontResolver


class PackageResourceTests(unittest.TestCase):
    def test_public_package_api_is_importable(self):
        self.assertEqual(wordpaper_core.__version__, "0.1.0")
        self.assertIsNotNone(wordpaper_core.Wallpaper)
        self.assertIsNotNone(wordpaper_core.PillowRenderer)

    def test_all_bundled_textures_are_resolvable(self):
        resolver = create_default_asset_resolver()

        for asset_id in DEFAULT_ASSET_PATHS:
            with self.subTest(asset_id=asset_id):
                self.assertTrue(resolver.resolve(AssetRef(asset_id)).is_file())

    def test_all_bundled_fonts_are_resolvable(self):
        resolver = PillowFontResolver.create_default()
        font_ids = (
            "playfair_display",
            "newsreader",
            "unifraktur_cook",
            "shrikhand",
            "modak",
            "metal_mania",
            "orbitron",
            "noto_sans",
        )

        for font_id in font_ids:
            with self.subTest(font_id=font_id):
                resolved = resolver.resolve(
                    Font(font_id, size_ratio=0.05, weight=FontWeight.BOLD),
                    canvas_width=1000,
                )
                self.assertGreater(resolved.size, 0)

    def test_ipa_transcription_uses_complete_fallback_font(self):
        resolver = PillowFontResolver.create_default()
        selected = Font(
            "playfair_display",
            size_ratio=0.05,
            weight=FontWeight.BOLD,
        )

        resolved = resolver.resolve_for_text(
            selected,
            canvas_width=1000,
            value="[kənˈsɪstənsi]",
        )

        self.assertTrue(resolver.supports_text(resolved, "[kənˈsɪstənsi]"))
        self.assertTrue(str(resolved.path).endswith("NotoSans.ttf"))


if __name__ == "__main__":
    unittest.main()
