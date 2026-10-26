from dataclasses import dataclass
from hashlib import blake2b
import random
import secrets

from wordpaper_core import AnchorPosition

from wordpaper_api.schemas import GenerationRequest, WallpaperSpec


@dataclass(frozen=True)
class Recipe:
    id: str
    label: str
    fonts: tuple[str, ...]
    anchors: tuple[str, ...]
    light_backgrounds: tuple[tuple[str, str | None], ...]
    dark_backgrounds: tuple[tuple[str, str | None], ...]
    effects: tuple[str, ...]
    font_sizes: tuple[float, ...]


ALL_ANCHORS = tuple(position.value for position in AnchorPosition)
EDGE_ANCHORS = (
    AnchorPosition.TOP_LEFT.value,
    AnchorPosition.TOP_RIGHT.value,
    AnchorPosition.BOTTOM_LEFT.value,
    AnchorPosition.BOTTOM_RIGHT.value,
    AnchorPosition.LEFT_CENTER.value,
    AnchorPosition.RIGHT_CENTER.value,
    AnchorPosition.BOTTOM_CENTER.value,
)

RECIPES: dict[str, Recipe] = {
    "editorial_dictionary": Recipe(
        id="editorial_dictionary",
        label="Editorial dictionary",
        fonts=("playfair_display", "newsreader"),
        anchors=(AnchorPosition.BOTTOM_LEFT.value, AnchorPosition.TOP_LEFT.value),
        light_backgrounds=(("#f4f1eb", None), ("#e8e4dc", None)),
        dark_backgrounds=(("#101010", None), ("#192126", None)),
        effects=("solid",),
        font_sizes=(0.055, 0.06, 0.067),
    ),
    "liquid_sky": Recipe(
        id="liquid_sky",
        label="Liquid sky",
        fonts=("playfair_display", "newsreader"),
        anchors=(AnchorPosition.BOTTOM_LEFT.value, AnchorPosition.CENTER.value),
        light_backgrounds=(
            ("#81b7da", "sky.clouds.soft"),
            ("#78aeda", "sky.clouds.fluffy"),
        ),
        dark_backgrounds=(
            ("#16324d", "sky.clouds.dense"),
            ("#0f3459", "sky.clouds.soft"),
        ),
        effects=("liquid_glass",),
        font_sizes=(0.058, 0.064, 0.07),
    ),
    "quiet_minimal": Recipe(
        id="quiet_minimal",
        label="Quiet minimal",
        fonts=("newsreader", "playfair_display"),
        anchors=(AnchorPosition.CENTER.value,) + EDGE_ANCHORS,
        light_backgrounds=(("#eee9df", None), ("#dfe5e1", None), ("#ebe4ed", None)),
        dark_backgrounds=(("#151719", None), ("#20231f", None), ("#241f25", None)),
        effects=("solid",),
        font_sizes=(0.045, 0.052, 0.058),
    ),
    "brutalist_type": Recipe(
        id="brutalist_type",
        label="Brutalist type",
        fonts=("orbitron", "metal_mania"),
        anchors=ALL_ANCHORS,
        light_backgrounds=(
            ("#e9ff42", None),
            ("#f2eee5", "studio.liquid_chrome"),
            ("#ff6b49", "studio.risograph_grain"),
        ),
        dark_backgrounds=(
            ("#090909", "studio.liquid_chrome"),
            ("#251313", "studio.risograph_grain"),
            ("#101d28", None),
        ),
        effects=("solid",),
        font_sizes=(0.052, 0.06, 0.072),
    ),
    "soft_pop": Recipe(
        id="soft_pop",
        label="Soft pop",
        fonts=("shrikhand", "modak"),
        anchors=ALL_ANCHORS,
        light_backgrounds=(
            ("#f5d5dc", None),
            ("#d8ead2", "fur.white"),
            ("#dce8fa", "sky.clouds_sparse"),
            ("#e9f5ff", "studio.holographic_film"),
        ),
        dark_backgrounds=(("#42253d", None), ("#173c34", "nature.grass")),
        effects=("solid", "liquid_glass"),
        font_sizes=(0.06, 0.07, 0.08),
    ),
    "gothic_archive": Recipe(
        id="gothic_archive",
        label="Gothic archive",
        fonts=("unifraktur_cook", "metal_mania"),
        anchors=EDGE_ANCHORS,
        light_backgrounds=(("#d8c5a6", "leather.crocodile"), ("#dfd4c4", None)),
        dark_backgrounds=(("#12100f", "leather.black"), ("#1d1712", "leather.crocodile")),
        effects=("solid",),
        font_sizes=(0.06, 0.068, 0.075),
    ),
}


def derive_seed(seed: int, index: int) -> int:
    digest = blake2b(f"{seed}:{index}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big") & ((1 << 63) - 1)


def generate_specs(request: GenerationRequest) -> tuple[int, list[WallpaperSpec]]:
    root_seed = request.seed if request.seed is not None else secrets.randbits(63)
    recipe_ids = tuple(RECIPES)
    specs: list[WallpaperSpec] = []

    for index in range(request.count):
        variant_seed = derive_seed(root_seed, index)
        rng = random.Random(variant_seed)
        recipe_id = request.recipe_id or rng.choice(recipe_ids)
        recipe = RECIPES.get(recipe_id)
        if recipe is None:
            raise ValueError(f"Unknown recipe: {recipe_id}")

        theme = request.theme if request.theme != "auto" else rng.choice(("light", "dark"))
        background_pool = (
            recipe.light_backgrounds if theme == "light" else recipe.dark_backgrounds
        )
        background_color, background_asset_id = rng.choice(background_pool)
        text_colors = (
            ("#101214", "#2b1b3c", "#15384c", "#7a1f35")
            if theme == "light"
            else ("#f5f3ed", "#e7f7ff", "#ffc6df", "#d6ff72")
        )
        text_color = rng.choice(text_colors)
        text_effect = rng.choice(recipe.effects)

        if request.intensity < 34:
            anchor_pool = recipe.anchors[: min(2, len(recipe.anchors))]
        elif request.intensity > 72:
            anchor_pool = ALL_ANCHORS
        else:
            anchor_pool = recipe.anchors

        spec = WallpaperSpec(
            seed=variant_seed,
            recipe_id=recipe.id,
            theme=theme,
            content=request.content,
            aspect_ratio=request.aspect_ratio,
            anchor=rng.choice(anchor_pool),
            font_id=rng.choice(recipe.fonts),
            font_size_ratio=rng.choice(recipe.font_sizes),
            text_color=text_color,
            text_effect=text_effect,
            glass_intensity=(
                rng.choice((0.4, 0.58, 0.76, 0.92, 1.0))
                if text_effect == "liquid_glass"
                else 0.72
            ),
            background_color=background_color,
            background_asset_id=background_asset_id,
        )

        if request.base_spec is not None:
            updates: dict[str, object] = {}
            if "font" in request.locks:
                updates.update(
                    font_id=request.base_spec.font_id,
                    font_size_ratio=request.base_spec.font_size_ratio,
                    text_color=request.base_spec.text_color,
                )
            if "background" in request.locks:
                updates.update(
                    background_color=request.base_spec.background_color,
                    background_asset_id=request.base_spec.background_asset_id,
                    theme=request.base_spec.theme,
                )
            if "layout" in request.locks:
                updates["anchor"] = request.base_spec.anchor
            if "effect" in request.locks:
                updates.update(
                    text_effect=request.base_spec.text_effect,
                    glass_intensity=request.base_spec.glass_intensity,
                )
            spec = spec.model_copy(update=updates)

        specs.append(spec)

    return root_seed, specs


def recipe_options() -> list[tuple[str, str]]:
    return [(recipe.id, recipe.label) for recipe in RECIPES.values()]
