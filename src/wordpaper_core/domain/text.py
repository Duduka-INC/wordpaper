from dataclasses import dataclass
from wordpaper_core.domain.font import Font
from wordpaper_core.domain.operation_plan import OperationPipeline
from wordpaper_core.domain.text_layout import TextLayout


@dataclass(frozen=True)
class Text:
    text: str
    description: str
    font: Font
    operation_pipeline: OperationPipeline
    layout: TextLayout
    transcription: str | None = None
    underline: bool = False
    part_of_speech: str | None = None
    language: str | None = None
