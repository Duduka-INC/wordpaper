from src.domain.export_request import ExportRequest, ExportFormat
from src.exporting.exporter import Exporter
from src.exporting.raster_exporter import RasterExporter


class ExportService:

    def __init__(self, exporters: dict[ExportFormat, Exporter]):
        self.exporters = exporters

    def export(self, request: ExportRequest):
        exporter = self.exporters.get(request.export_format)

        if exporter is None:
            raise ValueError(f"Unknown export format: {request.export_format}")

        return exporter.export(request)


    @staticmethod
    def create_default():
        raster_exporter = RasterExporter.create_default()

        exporters = {
            ExportFormat.PNG: raster_exporter,
            ExportFormat.JPEG: raster_exporter,
            ExportFormat.WEBP: raster_exporter,
        }

        return ExportService(exporters)