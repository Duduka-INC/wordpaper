from hashlib import sha256
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from wordpaper_core import (
    AnchorPosition,
    AspectRatio,
    AssetRef,
    Background,
    EdgeInsets,
    Font,
    FontWeight,
    ImageFillOperation,
    ImageFit,
    LiquidGlassOperation,
    OperationPipeline,
    PillowRenderer,
    RenderSize,
    ResponsiveMargins,
    SolidFillOperation,
    Text,
    TextLayout,
    Wallpaper,
)

from wordpaper_api.schemas import WallpaperSpec


CONTENT_TYPES = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}


def to_domain(spec: WallpaperSpec) -> Wallpaper:
    background_operations = [
        SolidFillOperation(fill_color=spec.background_color),
    ]
    if spec.background_asset_id:
        background_operations.append(
            ImageFillOperation(
                asset=AssetRef(spec.background_asset_id),
                fit=ImageFit.COVER,
            )
        )

    if spec.text_effect == "liquid_glass":
        text_operations = [
            LiquidGlassOperation(
                intensity=spec.glass_intensity,
                tint_color=spec.text_color,
            )
        ]
    else:
        text_operations = [SolidFillOperation(fill_color=spec.text_color)]

    margins = ResponsiveMargins(
        landscape=EdgeInsets(top=0.055, right=0.055, bottom=0.11, left=0.055),
        portrait=EdgeInsets(top=0.04, right=0.04, bottom=0.055, left=0.04),
    )
    return Wallpaper(
        text=Text(
            text=spec.content.word,
            transcription=spec.content.transcription,
            part_of_speech=spec.content.part_of_speech,
            language=spec.content.language,
            description=spec.content.definition,
            font=Font(
                font_id=spec.font_id,
                size_ratio=spec.font_size_ratio,
                weight=FontWeight.BOLD,
            ),
            operation_pipeline=OperationPipeline(text_operations),
            layout=TextLayout(
                position=AnchorPosition(spec.anchor),
                margins=margins,
            ),
            underline=spec.underline,
        ),
        background=Background(OperationPipeline(background_operations)),
        aspect_ratio=AspectRatio(
            width=spec.aspect_ratio.width,
            height=spec.aspect_ratio.height,
        ),
    )


def encode_spec(
    spec: WallpaperSpec,
    width: int,
    height: int,
    image_format: str,
    quality: int = 92,
) -> tuple[bytes, str, str]:
    artifact = PillowRenderer.create_default().render(
        to_domain(spec),
        RenderSize(width=width, height=height),
    )
    image = Image.frombytes(
        "RGBA",
        (artifact.width, artifact.height),
        artifact.pixels,
    )
    if image_format == "jpeg":
        image = image.convert("RGB")

    output = BytesIO()
    save_format = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}[image_format]
    save_options = {"quality": quality} if image_format in {"jpeg", "webp"} else {}
    source = spec.content.source_url
    if source:
        encoded_source = quote(source, safe=":/?&=%#")
        description = (
            f"Definition source: {encoded_source}; "
            f"license: {spec.content.source_license or 'see source'}"
        )
        if image_format == "png":
            png_info = PngInfo()
            png_info.add_text("Description", description)
            save_options["pnginfo"] = png_info
        else:
            exif = Image.Exif()
            exif[270] = description
            save_options["exif"] = exif
    image.save(output, format=save_format, **save_options)
    data = output.getvalue()
    return data, CONTENT_TYPES[image_format], sha256(data).hexdigest()


def preview_size(spec: WallpaperSpec, longest_edge: int = 960) -> tuple[int, int]:
    ratio = spec.aspect_ratio
    if ratio.width >= ratio.height:
        return longest_edge, round(longest_edge * ratio.height / ratio.width)
    return round(longest_edge * ratio.width / ratio.height), longest_edge


def library_resources_root() -> Path:
    import wordpaper_core

    return Path(wordpaper_core.__file__).resolve().parent / "resources"
