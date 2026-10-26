from collections.abc import Mapping
from pathlib import Path

from PIL import ImageFont

from wordpaper_core.domain.font import Font, FontStyle, FontWeight


FontKey = tuple[str, FontWeight, FontStyle]


class PillowFontResolver:
    def __init__(self, font_files: Mapping[FontKey, str]):
        self._font_files = dict(font_files)

    @classmethod
    def create_default(cls):
        package_root = Path(__file__).resolve().parents[2]
        fonts_root = package_root / "resources" / "fonts"
        font_files: dict[FontKey, str] = {}

        cls._register_family(
            font_files,
            "playfair_display",
            fonts_root / "playfair_display" / "PlayfairDisplay.ttf",
            fonts_root / "playfair_display" / "PlayfairDisplay-Italic.ttf",
        )
        cls._register_family(
            font_files,
            "newsreader",
            fonts_root / "newsreader" / "Newsreader.ttf",
            fonts_root / "newsreader" / "Newsreader-Italic.ttf",
        )
        cls._register_family(
            font_files,
            "unifraktur_cook",
            fonts_root / "unifraktur_cook" / "UnifrakturCook-Bold.ttf",
        )
        cls._register_family(
            font_files,
            "shrikhand",
            fonts_root / "shrikhand" / "Shrikhand-Regular.ttf",
        )
        cls._register_family(
            font_files,
            "modak",
            fonts_root / "modak" / "Modak-Regular.ttf",
        )
        cls._register_family(
            font_files,
            "metal_mania",
            fonts_root / "metal_mania" / "MetalMania-Regular.ttf",
        )
        cls._register_family(
            font_files,
            "orbitron",
            fonts_root / "orbitron" / "Orbitron.ttf",
        )
        cls._register_family(
            font_files,
            "noto_sans",
            fonts_root / "noto_sans" / "NotoSans.ttf",
        )
        return cls(font_files)

    @staticmethod
    def _register_family(
        font_files: dict[FontKey, str],
        font_id: str,
        normal_file: Path,
        italic_file: Path | None = None,
    ) -> None:
        resolved_italic = italic_file or normal_file
        for weight in FontWeight:
            font_files[(font_id, weight, FontStyle.NORMAL)] = str(normal_file)
            font_files[(font_id, weight, FontStyle.ITALIC)] = str(resolved_italic)

    def resolve(self, font: Font, canvas_width: int) -> ImageFont.FreeTypeFont:
        key = (font.font_id.lower(), font.weight, font.style)
        font_file = self._font_files.get(key)
        if font_file is None:
            raise ValueError(
                "Unsupported font: "
                f"{font.font_id}, weight={font.weight}, style={font.style}"
            )

        font_size = max(1, round(canvas_width * font.size_ratio))
        resolved_font = ImageFont.truetype(font_file, font_size)
        self._apply_variations(resolved_font, font, font_size)
        return resolved_font

    def resolve_for_text(
        self,
        font: Font,
        canvas_width: int,
        value: str,
        fallback_font_id: str = "noto_sans",
    ) -> ImageFont.FreeTypeFont:
        resolved_font = self.resolve(font, canvas_width)
        if self.supports_text(resolved_font, value):
            return resolved_font

        fallback = Font(
            font_id=fallback_font_id,
            size_ratio=font.size_ratio,
            weight=font.weight,
            style=font.style,
        )
        resolved_fallback = self.resolve(fallback, canvas_width)
        if not self.supports_text(resolved_fallback, value):
            missing = "".join(
                character
                for character in dict.fromkeys(value)
                if not character.isspace()
                and not self._supports_character(resolved_fallback, character)
            )
            raise ValueError(f"No bundled font supports these characters: {missing!r}")
        return resolved_fallback

    @classmethod
    def supports_text(
        cls,
        font: ImageFont.FreeTypeFont,
        value: str,
    ) -> bool:
        return all(
            character.isspace() or cls._supports_character(font, character)
            for character in value
        )

    @staticmethod
    def _supports_character(
        font: ImageFont.FreeTypeFont,
        character: str,
    ) -> bool:
        missing_character = "\U0010ffff"
        missing_signature = (
            font.getbbox(missing_character),
            bytes(font.getmask(missing_character)),
        )
        character_signature = (
            font.getbbox(character),
            bytes(font.getmask(character)),
        )
        return character_signature != missing_signature

    @staticmethod
    def _apply_variations(
        resolved_font: ImageFont.FreeTypeFont,
        font: Font,
        font_size: int,
    ) -> None:
        weights = {
            FontWeight.REGULAR: 400,
            FontWeight.MEDIUM: 500,
            FontWeight.SEMIBOLD: 600,
            FontWeight.BOLD: 700,
        }

        try:
            axes = resolved_font.get_variation_axes()
        except OSError:
            return

        values = []
        for axis in axes:
            axis_name = axis["name"].decode("ascii", errors="ignore").lower()
            if axis_name == "weight":
                value = weights[font.weight]
            elif axis_name == "optical size":
                value = font_size
            else:
                value = axis["default"]

            values.append(
                min(axis["maximum"], max(axis["minimum"], value))
            )

        resolved_font.set_variation_by_axes(values)
