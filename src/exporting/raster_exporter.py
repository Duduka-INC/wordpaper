from src.domain.export_request import ExportRequest
from src.exporting.exporter import Exporter


class RasterExporter(Exporter):
    def export(self, request: ExportRequest):
        pass