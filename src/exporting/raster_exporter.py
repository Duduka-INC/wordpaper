from PIL import Image

from src.domain.export_request import ExportFormat
from src.domain.export_request import ExportRequest
from src.exporting.exporter import Exporter
from src.rendering.pillow.pillow_renderer import PillowRenderer
from src.rendering.pillow.raster_artifact import RasterArtifact
from src.rendering.pillow.renderer import Renderer
from src.rendering.render_size import RenderSize


PIL_FORMATS = {
    ExportFormat.PNG: "PNG",
    ExportFormat.JPEG: "JPEG",
    ExportFormat.WEBP: "WEBP",
}


class RasterExporter(Exporter):
    def __init__(self, renderer: Renderer[RasterArtifact]):
        self._renderer = renderer

    @classmethod
    def create_default(cls):
        return cls(PillowRenderer.create_default())

    def export(self, request: ExportRequest):
        pil_format = PIL_FORMATS.get(request.export_format)

        if pil_format is None:
            raise ValueError(
                f"Unsupported raster export format: {request.export_format}"
            )

        artifact = self._renderer.render(
            request.wallpaper,
            RenderSize(request.width, request.height),
        )
        image = Image.frombytes(
            "RGBA",
            (artifact.width, artifact.height),
            artifact.pixels,
        )

        if request.export_format is ExportFormat.JPEG:
            image = image.convert("RGB")

        image.save(request.output_path, format=pil_format)
