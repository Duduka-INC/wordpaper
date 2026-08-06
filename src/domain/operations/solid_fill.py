from dataclasses import dataclass
from src.domain.operations.operation import Operation


@dataclass(frozen=True)
class SolidFillOperation(Operation):
    fill_color: str
