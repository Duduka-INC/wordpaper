import unittest

from wordpaper_api.generation import generate_specs
from wordpaper_api.rendering import encode_spec
from wordpaper_api.schemas import GenerationRequest


class RenderingTests(unittest.TestCase):
    def test_spec_is_encoded_as_real_webp(self) -> None:
        _, specs = generate_specs(
            GenerationRequest(seed=24, count=1, recipe_id="editorial_dictionary")
        )

        data, content_type, checksum = encode_spec(
            specs[0],
            width=320,
            height=180,
            image_format="webp",
            quality=80,
        )

        self.assertTrue(data.startswith(b"RIFF"))
        self.assertEqual(content_type, "image/webp")
        self.assertEqual(len(checksum), 64)


if __name__ == "__main__":
    unittest.main()
