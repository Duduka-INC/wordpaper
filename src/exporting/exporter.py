from abc import ABC, abstractmethod

from src.domain.export_request import ExportRequest


class Exporter(ABC):
    @abstractmethod
    def export(self, request: ExportRequest):
        pass