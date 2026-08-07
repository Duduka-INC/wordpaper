from PIL import Image, ImageChops, ImageDraw

from src.domain.wallpaper import Wallpaper
from src.rendering.pillow.pillow_font_resolver import PillowFontResolver
from src.rendering.pillow.pillow_operation_executor import PillowOperationExecutor
from src.rendering.pillow.raster_artifact import RasterArtifact
from src.rendering.pillow.renderer import Renderer
from src.rendering.pillow.text_placement import resolve_text_placement
from src.rendering.render_size import RenderSize


class PillowRenderer(Renderer[RasterArtifact]):
    def __init__(
        self,
        operation_executor: PillowOperationExecutor,
        font_resolver: PillowFontResolver,
    ):
        self._operation_executor = operation_executor
        self._font_resolver = font_resolver

    @classmethod
    def create_default(cls):
        return cls(
            PillowOperationExecutor(),
            PillowFontResolver.create_default(),
        )

    def render(
        self,
        wallpaper: Wallpaper,
        render_size: RenderSize,
    ) -> RasterArtifact:
        canvas = Image.new("RGBA", (render_size.width, render_size.height))
        canvas = self._operation_executor.execute(
            canvas,
            wallpaper.background.operation_pipeline,
        )

        placement = resolve_text_placement(
            wallpaper.text.layout,
            canvas.width,
            canvas.height,
        )
        font = self._font_resolver.resolve(
            wallpaper.text.font,
            canvas.width,
        )

        text_mask = Image.new("L", canvas.size, 0)
        mask_draw = ImageDraw.Draw(text_mask)
        mask_draw.text(
            (placement.x, placement.y),
            wallpaper.text.text,
            font=font,
            fill=255,
            anchor=placement.anchor,
        )

        text_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        text_layer = self._operation_executor.execute(
            text_layer,
            wallpaper.text.operation_pipeline,
        )
        text_alpha = ImageChops.multiply(
            text_layer.getchannel("A"),
            text_mask,
        )
        text_layer.putalpha(text_alpha)
        canvas = Image.alpha_composite(canvas, text_layer)

        return RasterArtifact(
            width=canvas.width,
            height=canvas.height,
            pixels=canvas.tobytes(),
        )
