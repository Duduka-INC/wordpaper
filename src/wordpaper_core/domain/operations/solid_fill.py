from dataclasses import dataclass
from wordpaper_core.domain.operations.operation import Operation


@dataclass(frozen=True)
class SolidFillOperation(Operation):
    fill_color: str
