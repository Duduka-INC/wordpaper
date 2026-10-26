import shutil
import unittest
import uuid
from pathlib import Path

from PIL import Image

from wordpaper_core.assets.local_asset_resolver import LocalAssetResolver
from wordpaper_core.domain.asset_ref import AssetRef
from wordpaper_core.domain.image_fit import ImageFit
from wordpaper_core.domain.operation_plan import OperationPipeline
from wordpaper_core.domain.operations.image_fill import ImageFillOperation
from wordpaper_core.domain.operations.liquid_glass import LiquidGlassOperation
from wordpaper_core.rendering.pillow.pillow_operation_executor import (
    PillowOperationExecutor,
)


class PillowOperationExecutorTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path(__file__).resolve().parents[1] / ".tmp" / "tests"
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temporary_directory = temporary_root / str(uuid.uuid4())
        self.temporary_directory.mkdir()
        root = self.temporary_directory
        Image.new("RGBA", (4, 2), (255, 0, 0, 255)).save(root / "source.png")
        resolver = LocalAssetResolver(
            root_directory=root,
            asset_paths={"test.image": "source.png"},
        )
        self.executor = PillowOperationExecutor(resolver)

    def tearDown(self):
        shutil.rmtree(self.temporary_directory)

    def test_all_fit_modes_preserve_target_size(self):
        for fit in ImageFit:
            with self.subTest(fit=fit):
                target = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
                pipeline = OperationPipeline(
                    operations=[
                        ImageFillOperation(
                            asset=AssetRef("test.image"),
                            fit=fit,
                        )
                    ]
                )

                result = self.executor.execute(target, pipeline)

                self.assertEqual(result.mode, "RGBA")
                self.assertEqual(result.size, target.size)

    def test_contain_keeps_previous_layer_outside_image(self):
        target = Image.new("RGBA", (8, 8), (0, 0, 255, 255))
        pipeline = OperationPipeline(
            operations=[
                ImageFillOperation(
                    asset=AssetRef("test.image"),
                    fit=ImageFit.CONTAIN,
                )
            ]
        )

        result = self.executor.execute(target, pipeline)

        self.assertEqual(result.getpixel((0, 0)), (0, 0, 255, 255))
        self.assertEqual(result.getpixel((4, 4)), (255, 0, 0, 255))

    def test_liquid_glass_uses_backdrop_and_preserves_size(self):
        target = Image.new("RGBA", (32, 24), (0, 0, 0, 0))
        backdrop = Image.new("RGBA", target.size, (30, 120, 210, 255))
        mask = Image.new("L", target.size, 0)
        for y in range(6, 18):
            for x in range(8, 24):
                mask.putpixel((x, y), 255)

        result = self.executor.execute(
            target,
            OperationPipeline([LiquidGlassOperation()]),
            backdrop=backdrop,
            mask=mask,
        )

        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.size, target.size)
        self.assertNotEqual(result.getpixel((16, 12)), backdrop.getpixel((16, 12)))

    def test_liquid_glass_intensity_is_validated(self):
        with self.assertRaises(ValueError):
            LiquidGlassOperation(intensity=1.01)


if __name__ == "__main__":
    unittest.main()
