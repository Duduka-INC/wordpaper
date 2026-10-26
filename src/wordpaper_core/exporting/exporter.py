from abc import ABC, abstractmethod

from wordpaper_core.domain.export_request import ExportRequest


class Exporter(ABC):
    @abstractmethod
    def export(self, request: ExportRequest):
        pass
