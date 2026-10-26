from dataclasses import replace

from PIL import Image, ImageDraw, ImageFont

from wordpaper_core.domain.font import FontStyle, FontWeight
from wordpaper_core.domain.text import Text
from wordpaper_core.rendering.pillow.pillow_font_resolver import PillowFontResolver
from wordpaper_core.rendering.pillow.text_placement import resolve_text_placement


class PillowDictionaryTextRenderer:
    def __init__(self, font_resolver: PillowFontResolver):
        self._font_resolver = font_resolver

    def render_mask(
        self,
        text: Text,
        canvas_size: tuple[int, int],
    ) -> Image.Image:
        canvas_width, canvas_height = canvas_size
        block_width = self._resolve_block_width(text, canvas_size)
        block = self._render_block(text, canvas_size, block_width)
        placement = resolve_text_placement(
            text.layout,
            canvas_width,
            canvas_height,
            block.size,
        )

        mask = Image.new("L", canvas_size, 0)
        mask.paste(block, (placement.x, placement.y))
        return mask

    def _render_block(
        self,
        text: Text,
        canvas_size: tuple[int, int],
        block_width: int,
    ) -> Image.Image:
        canvas_width, canvas_height = canvas_size
        title_font = self._resolve_title_font(text, canvas_width, block_width)
        meta_size_ratio = max(0.018, text.font.size_ratio * 0.35)
        body_size_ratio = max(0.016, text.font.size_ratio * 0.33)
        meta_font = self._font_resolver.resolve_for_text(
            replace(
                text.font,
                size_ratio=meta_size_ratio,
                weight=FontWeight.SEMIBOLD,
                style=FontStyle.NORMAL,
            ),
            canvas_width,
            text.part_of_speech or "",
        )
        transcription_font = self._font_resolver.resolve_for_text(
            replace(
                text.font,
                size_ratio=meta_size_ratio,
                weight=FontWeight.SEMIBOLD,
                style=FontStyle.NORMAL,
            ),
            canvas_width,
            text.transcription or "",
        )
        meta_italic_font = self._font_resolver.resolve_for_text(
            replace(
                text.font,
                size_ratio=meta_size_ratio,
                weight=FontWeight.SEMIBOLD,
                style=FontStyle.ITALIC,
            ),
            canvas_width,
            text.language or "",
        )
        body_font = self._font_resolver.resolve_for_text(
            replace(
                text.font,
                size_ratio=body_size_ratio,
                weight=FontWeight.REGULAR,
                style=FontStyle.NORMAL,
            ),
            canvas_width,
            text.description or "",
        )

        working_height = max(canvas_width, canvas_height * 2, 1000)
        block = Image.new("L", (block_width, working_height), 0)
        draw = ImageDraw.Draw(block)
        y = 0

        y += self._draw_text_from_top(draw, (0, y), text.text, title_font)

        meta_segments = self._build_meta_segments(
            text,
            regular_font=meta_font,
            italic_font=meta_italic_font,
            transcription_font=transcription_font,
        )
        if meta_segments:
            y += round(canvas_width * 0.004)
            y += self._draw_segments_from_top(draw, y, meta_segments)

        if text.underline:
            y += round(canvas_width * 0.022)
            line_width = max(2, round(canvas_width * 0.002))
            draw.line((0, y, block_width, y), fill=255, width=line_width)
            y += line_width

        if text.description:
            y += round(canvas_width * 0.024)
            lines = self._wrap_text(
                draw,
                text.description,
                body_font,
                block_width,
            )
            line_spacing = round(canvas_width * 0.01)
            for index, line in enumerate(lines):
                y += self._draw_text_from_top(draw, (0, y), line, body_font)
                if index < len(lines) - 1:
                    y += line_spacing

        return block.crop((0, 0, block_width, max(1, y)))

    def _resolve_title_font(
        self,
        text: Text,
        canvas_width: int,
        block_width: int,
    ) -> ImageFont.FreeTypeFont:
        title_font = self._font_resolver.resolve_for_text(
            text.font,
            canvas_width,
            text.text,
        )
        title_width = title_font.getlength(text.text)
        if title_width <= block_width:
            return title_font

        fitted_ratio = text.font.size_ratio * block_width / title_width * 0.98
        return self._font_resolver.resolve_for_text(
            replace(text.font, size_ratio=max(0.003, fitted_ratio)),
            canvas_width,
            text.text,
        )

    @staticmethod
    def _resolve_block_width(
        text: Text,
        canvas_size: tuple[int, int],
    ) -> int:
        width, height = canvas_size
        margins = (
            text.layout.margins.portrait
            if width < height
            else text.layout.margins.landscape
        )
        safe_width = round(width * (1 - margins.left - margins.right))
        if width < height:
            return safe_width
        return min(safe_width, round(width * 0.47))

    @staticmethod
    def _build_meta_segments(
        text: Text,
        regular_font: ImageFont.FreeTypeFont,
        italic_font: ImageFont.FreeTypeFont,
        transcription_font: ImageFont.FreeTypeFont,
    ) -> list[tuple[str, ImageFont.FreeTypeFont]]:
        segments: list[tuple[str, ImageFont.FreeTypeFont]] = []

        if text.transcription:
            segments.append((text.transcription, transcription_font))

        if text.part_of_speech:
            if segments:
                segments.append(("  ", regular_font))
            segments.append((text.part_of_speech, regular_font))

        if text.language:
            if segments:
                segments.append(("  •  ", regular_font))
            segments.append((text.language, italic_font))

        return segments

    @staticmethod
    def _draw_segments_from_top(
        draw: ImageDraw.ImageDraw,
        y: int,
        segments: list[tuple[str, ImageFont.FreeTypeFont]],
    ) -> int:
        metrics = [font.getmetrics() for _, font in segments]
        max_ascent = max(ascent for ascent, _ in metrics)
        max_descent = max(descent for _, descent in metrics)
        baseline = y + max_ascent
        x = 0.0
        for value, font in segments:
            draw.text(
                (round(x), baseline),
                value,
                font=font,
                fill=255,
                anchor="ls",
            )
            x += draw.textlength(value, font=font)
        return max_ascent + max_descent

    @staticmethod
    def _draw_text_from_top(
        draw: ImageDraw.ImageDraw,
        position: tuple[int, int],
        value: str,
        font: ImageFont.FreeTypeFont,
    ) -> int:
        x, y = position
        left, top, right, bottom = draw.textbbox((0, 0), value, font=font)
        draw.text((x - left, y - top), value, font=font, fill=255)
        return bottom - top

    @staticmethod
    def _wrap_text(
        draw: ImageDraw.ImageDraw,
        value: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
    ) -> list[str]:
        words = value.split()
        if not words:
            return []

        lines: list[str] = []
        current_line = words[0]

        for word in words[1:]:
            candidate = f"{current_line} {word}"
            if draw.textlength(candidate, font=font) <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word

        lines.append(current_line)
        return lines
