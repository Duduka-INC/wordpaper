from dataclasses import dataclass
from src.domain.operation_plan import OperationPipeline


@dataclass(frozen=True)
class Background:
    operation_pipeline: OperationPipeline
