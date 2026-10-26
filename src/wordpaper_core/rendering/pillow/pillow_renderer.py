from PIL import Image, ImageChops

from wordpaper_core.domain.wallpaper import Wallpaper
from wordpaper_core.rendering.pillow.pillow_dictionary_text_renderer import (
    PillowDictionaryTextRenderer,
)
from wordpaper_core.rendering.pillow.pillow_font_resolver import PillowFontResolver
from wordpaper_core.rendering.pillow.pillow_operation_executor import PillowOperationExecutor
from wordpaper_core.rendering.pillow.raster_artifact import RasterArtifact
from wordpaper_core.rendering.pillow.renderer import Renderer
from wordpaper_core.rendering.render_size import RenderSize


class PillowRenderer(Renderer[RasterArtifact]):
    def __init__(
        self,
        operation_executor: PillowOperationExecutor,
        text_renderer: PillowDictionaryTextRenderer,
    ):
        self._operation_executor = operation_executor
        self._text_renderer = text_renderer

    @classmethod
    def create_default(cls):
        font_resolver = PillowFontResolver.create_default()
        return cls(
            PillowOperationExecutor.create_default(),
            PillowDictionaryTextRenderer(font_resolver),
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

        text_mask = self._text_renderer.render_mask(
            wallpaper.text,
            canvas.size,
        )

        text_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        text_layer = self._operation_executor.execute(
            text_layer,
            wallpaper.text.operation_pipeline,
            backdrop=canvas,
            mask=text_mask,
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
