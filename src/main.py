from src.domain.background import Background
from src.domain.anchor_position import AnchorPosition
from src.domain.aspect_ratio import AspectRatio
from src.domain.export_request import ExportFormat, ExportRequest
from src.domain.font import Font, FontStyle, FontWeight
from src.domain.operation_plan import OperationPipeline
from src.domain.operations.solid_fill import SolidFillOperation
from src.domain.text import Text
from src.domain.text_layout import EdgeInsets, ResponsiveMargins, TextLayout
from src.domain.wallpaper import Wallpaper
from src.export_service import ExportService


background_pipeline = OperationPipeline(
    operations=[SolidFillOperation(fill_color="#336699")]
)
text_pipeline = OperationPipeline(
    operations=[SolidFillOperation(fill_color="#ffffff")]
)

text = Text(
    text="consistency",
    description="the ability to repeat a process with the same quality",
    font=Font(
        font_id="arial",
        size_ratio=0.05,
        weight=FontWeight.REGULAR,
        style=FontStyle.NORMAL,
    ),
    operation_pipeline=text_pipeline,
    layout=TextLayout(
        position=AnchorPosition.BOTTOM_LEFT,
        margins=ResponsiveMargins(
            landscape=EdgeInsets(
                top=0.06,
                right=0.055,
                bottom=0.09,
                left=0.055,
            ),
            portrait=EdgeInsets(
                top=0.035,
                right=0.035,
                bottom=0.04,
                left=0.035,
            ),
        ),
    ),
    transcription=False,
    underline=False,
)

wallpaper = Wallpaper(
    text=text,
    background=Background(operation_pipeline=background_pipeline),
    aspect_ratio=AspectRatio(width=16, height=9),
)

request = ExportRequest(
    wallpaper=wallpaper,
    export_format=ExportFormat.PNG,
    output_path="wallpaper.png",
    width=1920,
    height=1080,
)

ExportService.create_default().export(request)
print(f"Exported: {request.output_path}")
