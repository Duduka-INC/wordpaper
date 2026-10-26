from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Theme = Literal["light", "dark"]
ExportFormat = Literal["png", "jpeg", "webp"]
Visibility = Literal["private", "unlisted", "public"]


class ContentSpec(BaseModel):
    word: str = Field(default="consistency", max_length=80)
    transcription: str | None = Field(default=None, max_length=120)
    part_of_speech: str | None = Field(default=None, max_length=40)
    language: str | None = Field(default=None, max_length=40)
    definition: str = Field(default="", max_length=700)


class AspectRatioSpec(BaseModel):
    width: int = Field(default=16, ge=1, le=100)
    height: int = Field(default=9, ge=1, le=100)


class WallpaperSpec(BaseModel):
    schema_version: int = 1
    seed: int
    recipe_id: str
    theme: Theme
    content: ContentSpec
    aspect_ratio: AspectRatioSpec = Field(default_factory=AspectRatioSpec)
    anchor: str = "bottom_left"
    font_id: str = "playfair_display"
    font_size_ratio: float = Field(default=0.06, gt=0.015, lt=0.2)
    text_color: str = "#111111"
    text_effect: Literal["solid", "liquid_glass"] = "solid"
    glass_intensity: float = Field(default=0.72, ge=0, le=1)
    background_color: str = "#f2efe8"
    background_asset_id: str | None = None
    underline: bool = True


class GenerationRequest(BaseModel):
    content: ContentSpec = Field(default_factory=ContentSpec)
    theme: Literal["light", "dark", "auto"] = "auto"
    recipe_id: str | None = None
    aspect_ratio: AspectRatioSpec = Field(default_factory=AspectRatioSpec)
    count: int = Field(default=4, ge=1, le=4)
    seed: int | None = None
    intensity: int = Field(default=48, ge=0, le=100)
    locks: list[Literal["font", "background", "layout", "effect"]] = Field(
        default_factory=list
    )
    base_spec: WallpaperSpec | None = None


class GeneratedVariant(BaseModel):
    variant_id: str
    spec: WallpaperSpec
    preview_url: str


class GenerationResponse(BaseModel):
    seed: int
    variants: list[GeneratedVariant]


class CreateWallRequest(BaseModel):
    spec: WallpaperSpec
    visibility: Visibility = "public"


class UpdateWallRequest(BaseModel):
    spec: WallpaperSpec
    expected_revision: int = Field(ge=1)


class CreateRenderRequest(BaseModel):
    resolution: Literal["1080p", "2k", "4k", "8k", "custom"] = "1080p"
    format: ExportFormat = "webp"
    quality: int = Field(default=92, ge=60, le=100)
    width: int | None = Field(default=None, ge=320, le=7680)
    height: int | None = Field(default=None, ge=320, le=7680)

    @model_validator(mode="after")
    def validate_custom_resolution(self):
        if self.resolution == "custom" and (self.width is None or self.height is None):
            raise ValueError("Custom resolution requires both width and height")
        return self


class RenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    kind: str
    width: int
    height: int
    format: str
    status: str
    url: str | None
    download_url: str | None
    byte_size: int | None
    created_at: datetime


class WallOut(BaseModel):
    wall_id: str
    visibility: str
    revision: int
    is_owner: bool
    spec: WallpaperSpec
    cover_url: str | None
    export_count: int
    created_at: datetime
    updated_at: datetime
    renders: list[RenderOut] = Field(default_factory=list)


class GalleryItem(BaseModel):
    wall_id: str
    theme: Theme
    word: str
    recipe_id: str
    cover_url: str
    aspect_ratio: AspectRatioSpec
    export_count: int


class GalleryResponse(BaseModel):
    items: list[GalleryItem]
    next_cursor: str | None


class MetaOption(BaseModel):
    id: str
    label: str


class MetaResponse(BaseModel):
    fonts: list[MetaOption]
    textures: list[MetaOption]
    recipes: list[MetaOption]
    anchors: list[MetaOption]
    resolutions: list[MetaOption]
