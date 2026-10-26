from wordpaper_core import (
    AnchorPosition,
    AspectRatio,
    AssetRef,
    Background,
    EdgeInsets,
    ExportFormat,
    ExportRequest,
    ExportService,
    Font,
    FontStyle,
    FontWeight,
    ImageFillOperation,
    ImageFit,
    LiquidGlassOperation,
    OperationPipeline,
    ResolutionPreset,
    ResponsiveMargins,
    SolidFillOperation,
    Text,
    TextLayout,
    Wallpaper,
)


def main() -> None:
    wallpaper = Wallpaper(
        text=Text(
            text="consistency",
            transcription="[kən-sis-tən-sē]",
            part_of_speech="noun",
            language="English",
            description=(
                "the ability to replicate a process or activity with the same "
                "level or quality over and over again. the adherence of the same "
                "principles in a steadfast way. consistency is what transforms "
                "average into excellence."
            ),
            font=Font(
                font_id="playfair_display",
                size_ratio=0.06,
                weight=FontWeight.BOLD,
                style=FontStyle.NORMAL,
            ),
            operation_pipeline=OperationPipeline(
                operations=[LiquidGlassOperation()]
            ),
            layout=TextLayout(
                position=AnchorPosition.BOTTOM_LEFT,
                margins=ResponsiveMargins(
                    landscape=EdgeInsets(
                        top=0.06,
                        right=0.055,
                        bottom=0.145,
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
            underline=True,
        ),
        background=Background(
            operation_pipeline=OperationPipeline(
                operations=[
                    SolidFillOperation(fill_color="#7db6df"),
                    ImageFillOperation(
                        asset=AssetRef("sky.clouds.soft"),
                        fit=ImageFit.COVER,
                    ),
                ]
            )
        ),
        aspect_ratio=AspectRatio(width=16, height=9),
    )

    request = ExportRequest.from_preset(
        wallpaper=wallpaper,
        export_format=ExportFormat.PNG,
        output_path="wallpaper.png",
        resolution_preset=ResolutionPreset.UHD_4K,
    )

    ExportService.create_default().export(request)
    print(f"Exported: {request.output_path} ({request.width}x{request.height})")


if __name__ == "__main__":
    main()
