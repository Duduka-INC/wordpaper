from dataclasses import dataclass
from src.domain.font import Font
from src.domain.operation_plan import OperationPipeline


@dataclass(frozen=True)
class Text:
    text: str
    description: str
    font: Font
    operation_pipeline: OperationPipeline
    transcription: bool
    underline: bool