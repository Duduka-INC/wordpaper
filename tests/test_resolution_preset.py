import unittest

from wordpaper_core.domain.aspect_ratio import AspectRatio
from wordpaper_core.domain.resolution_preset import Resolution, ResolutionPreset


class ResolutionPresetTests(unittest.TestCase):
    def test_resolves_standard_landscape_sizes(self):
        expected = {
            ResolutionPreset.FULL_HD: Resolution(1920, 1080),
            ResolutionPreset.QHD_2K: Resolution(2560, 1440),
            ResolutionPreset.UHD_4K: Resolution(3840, 2160),
            ResolutionPreset.UHD_8K: Resolution(7680, 4320),
        }

        for preset, resolution in expected.items():
            with self.subTest(preset=preset):
                self.assertEqual(
                    preset.resolve(AspectRatio(16, 9)),
                    resolution,
                )

    def test_swaps_dimensions_for_portrait_wallpaper(self):
        self.assertEqual(
            ResolutionPreset.UHD_4K.resolve(AspectRatio(9, 16)),
            Resolution(2160, 3840),
        )

    def test_preserves_non_standard_aspect_ratio(self):
        self.assertEqual(
            ResolutionPreset.FULL_HD.resolve(AspectRatio(4, 3)),
            Resolution(1920, 1440),
        )


if __name__ == "__main__":
    unittest.main()
