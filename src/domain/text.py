from dataclasses import dataclass
from src.domain.font import Font
from src.domain.operation_plan import OperationPipeline
from src.domain.text_layout import TextLayout


@dataclass(frozen=True)
class Text:
    text: str
    description: str
    font: Font
    operation_pipeline: OperationPipeline
    layout: TextLayout
    transcription: bool
    underline: bool
