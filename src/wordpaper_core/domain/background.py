from dataclasses import dataclass
from wordpaper_core.domain.operation_plan import OperationPipeline


@dataclass(frozen=True)
class Background:
    operation_pipeline: OperationPipeline
