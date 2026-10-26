import unittest

from wordpaper_api.generation import generate_specs
from wordpaper_api.schemas import GenerationRequest


class GenerationTests(unittest.TestCase):
    def test_same_seed_produces_the_same_specs(self) -> None:
        request = GenerationRequest(seed=42, count=4)

        first_seed, first = generate_specs(request)
        second_seed, second = generate_specs(request)

        self.assertEqual(first_seed, second_seed)
        self.assertEqual(first, second)
        self.assertEqual(len({spec.seed for spec in first}), 4)

    def test_locks_keep_selected_properties(self) -> None:
        _, base = generate_specs(
            GenerationRequest(seed=7, count=1, recipe_id="liquid_sky")
        )
        request = GenerationRequest(
            seed=8,
            count=4,
            base_spec=base[0],
            locks=["font", "background", "layout", "effect"],
        )

        _, variants = generate_specs(request)

        for variant in variants:
            self.assertEqual(variant.font_id, base[0].font_id)
            self.assertEqual(variant.text_color, base[0].text_color)
            self.assertEqual(variant.background_color, base[0].background_color)
            self.assertEqual(variant.background_asset_id, base[0].background_asset_id)
            self.assertEqual(variant.anchor, base[0].anchor)
            self.assertEqual(variant.text_effect, base[0].text_effect)
            self.assertEqual(variant.glass_intensity, base[0].glass_intensity)


if __name__ == "__main__":
    unittest.main()
