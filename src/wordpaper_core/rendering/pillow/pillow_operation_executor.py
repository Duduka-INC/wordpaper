from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

from wordpaper_core.assets.default_asset_catalog import create_default_asset_resolver
from wordpaper_core.assets.local_asset_resolver import LocalAssetResolver
from wordpaper_core.domain.image_fit import ImageFit
from wordpaper_core.domain.operation_plan import OperationPipeline
from wordpaper_core.domain.operations.image_fill import ImageFillOperation
from wordpaper_core.domain.operations.liquid_glass import LiquidGlassOperation
from wordpaper_core.domain.operations.operation import Operation
from wordpaper_core.domain.operations.solid_fill import SolidFillOperation


class PillowOperationExecutor:
    def __init__(self, asset_resolver: LocalAssetResolver):
        self._asset_resolver = asset_resolver

    @classmethod
    def create_default(cls):
        return cls(create_default_asset_resolver())

    def execute(
        self,
        target: Image.Image,
        pipeline: OperationPipeline,
        *,
        backdrop: Image.Image | None = None,
        mask: Image.Image | None = None,
    ) -> Image.Image:
        current = target

        for operation in pipeline.operations:
            current = self._apply(
                current,
                operation,
                backdrop=backdrop,
                mask=mask,
            )

        return current

    def _apply(
        self,
        target: Image.Image,
        operation: Operation,
        *,
        backdrop: Image.Image | None,
        mask: Image.Image | None,
    ) -> Image.Image:
        if isinstance(operation, SolidFillOperation):
            return self._apply_solid_fill(target, operation)

        if isinstance(operation, ImageFillOperation):
            return self._apply_image_fill(target, operation)

        if isinstance(operation, LiquidGlassOperation):
            return self._apply_liquid_glass(
                target,
                operation,
                backdrop=backdrop,
                mask=mask,
            )

        raise NotImplementedError(
            f"Unsupported Pillow operation: {type(operation).__name__}"
        )

    @staticmethod
    def _apply_solid_fill(
        target: Image.Image,
        operation: SolidFillOperation,
    ) -> Image.Image:
        return Image.new(target.mode, target.size, operation.fill_color)

    def _apply_image_fill(
        self,
        target: Image.Image,
        operation: ImageFillOperation,
    ) -> Image.Image:
        asset_path = self._asset_resolver.resolve(operation.asset)

        with Image.open(asset_path) as source_image:
            source = source_image.convert("RGBA")

        layer = self._fit_image(
            source=source,
            target_size=target.size,
            fit=operation.fit,
        )
        return Image.alpha_composite(target.convert("RGBA"), layer)

    @staticmethod
    def _apply_liquid_glass(
        target: Image.Image,
        operation: LiquidGlassOperation,
        *,
        backdrop: Image.Image | None,
        mask: Image.Image | None,
    ) -> Image.Image:
        source = backdrop if backdrop is not None else target
        source = source.convert("RGBA")
        if source.size != target.size:
            source = source.resize(target.size, Image.Resampling.LANCZOS)

        scale = min(target.size)
        intensity = operation.intensity
        blur_radius = max(
            0.0,
            scale * operation.blur_radius_ratio * intensity,
        )
        refraction_offset = max(
            0,
            round(scale * operation.refraction_offset_ratio * intensity),
        )
        edge_width = max(1, round(scale * operation.edge_width_ratio))

        glass = source.filter(ImageFilter.GaussianBlur(blur_radius))
        glass = PillowOperationExecutor._add_chromatic_refraction(
            glass,
            refraction_offset,
        )
        glass = ImageEnhance.Contrast(glass).enhance(1 + 0.12 * intensity)
        glass = ImageEnhance.Brightness(glass).enhance(1 + 0.06 * intensity)

        tint = Image.new("RGBA", target.size, operation.tint_color)
        tint.putalpha(round(255 * operation.tint_opacity * intensity))
        glass = Image.alpha_composite(glass, tint)

        if mask is not None:
            shape = mask.convert("L")
            highlight = ImageChops.subtract(
                shape,
                PillowOperationExecutor._translate_mask(
                    shape,
                    edge_width,
                    edge_width,
                ),
            )
            shadow = ImageChops.subtract(
                shape,
                PillowOperationExecutor._translate_mask(
                    shape,
                    -edge_width,
                    -edge_width,
                ),
            )
            edge_blur = max(0.5, edge_width * 0.55)
            highlight = highlight.filter(ImageFilter.GaussianBlur(edge_blur))
            shadow = shadow.filter(ImageFilter.GaussianBlur(edge_blur))

            shadow_layer = Image.new("RGBA", target.size, (7, 24, 38, 0))
            shadow_layer.putalpha(
                shadow.point(
                    lambda value: round(
                        value * operation.shadow_opacity * intensity
                    )
                )
            )
            glass = Image.alpha_composite(glass, shadow_layer)

            highlight_layer = Image.new("RGBA", target.size, (255, 255, 255, 0))
            highlight_layer.putalpha(
                highlight.point(
                    lambda value: round(
                        value * operation.highlight_opacity * intensity
                    )
                )
            )
            glass = Image.alpha_composite(glass, highlight_layer)

        return glass

    @staticmethod
    def _add_chromatic_refraction(
        source: Image.Image,
        offset: int,
    ) -> Image.Image:
        red, green, blue, alpha = source.split()
        red = PillowOperationExecutor._translate_channel(red, -offset, 0)
        blue = PillowOperationExecutor._translate_channel(blue, offset, 0)
        return Image.merge("RGBA", (red, green, blue, alpha))

    @staticmethod
    def _translate_mask(
        source: Image.Image,
        x: int,
        y: int,
    ) -> Image.Image:
        return source.transform(
            source.size,
            Image.Transform.AFFINE,
            (1, 0, -x, 0, 1, -y),
            resample=Image.Resampling.BILINEAR,
            fillcolor=0,
        )

    @staticmethod
    def _translate_channel(
        source: Image.Image,
        x: int,
        y: int,
    ) -> Image.Image:
        return source.transform(
            source.size,
            Image.Transform.AFFINE,
            (1, 0, -x, 0, 1, -y),
            resample=Image.Resampling.BILINEAR,
            fillcolor=0,
        )

    @staticmethod
    def _fit_image(
        source: Image.Image,
        target_size: tuple[int, int],
        fit: ImageFit,
    ) -> Image.Image:
        if fit is ImageFit.COVER:
            return ImageOps.fit(
                source,
                target_size,
                method=Image.Resampling.LANCZOS,
            )

        if fit is ImageFit.STRETCH:
            return source.resize(
                target_size,
                resample=Image.Resampling.LANCZOS,
            )

        layer = Image.new("RGBA", target_size, (0, 0, 0, 0))

        if fit is ImageFit.CONTAIN:
            contained = ImageOps.contain(
                source,
                target_size,
                method=Image.Resampling.LANCZOS,
            )
            position = (
                (target_size[0] - contained.width) // 2,
                (target_size[1] - contained.height) // 2,
            )
            layer.alpha_composite(contained, dest=position)
            return layer

        if fit is ImageFit.TILE:
            for y in range(0, target_size[1], source.height):
                for x in range(0, target_size[0], source.width):
                    layer.alpha_composite(source, dest=(x, y))
            return layer

        raise ValueError(f"Unsupported image fit: {fit}")
