import unittest
from io import BytesIO

from PIL import Image

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

    def test_definition_source_is_embedded_in_png_metadata(self) -> None:
        _, specs = generate_specs(GenerationRequest(seed=25, count=1))
        spec = specs[0].model_copy(
            update={
                "content": specs[0].content.model_copy(
                    update={
                        "source_name": "Русский Викисловарь",
                        "source_url": "https://ru.wiktionary.org/wiki/слово",
                        "source_license": "CC BY-SA 4.0 / GFDL",
                    }
                )
            }
        )

        data, _, _ = encode_spec(spec, 320, 180, "png")
        image = Image.open(BytesIO(data))

        self.assertIn("ru.wiktionary.org/wiki/", image.info["Description"])
        self.assertIn("CC BY-SA 4.0", image.info["Description"])


if __name__ == "__main__":
    unittest.main()
