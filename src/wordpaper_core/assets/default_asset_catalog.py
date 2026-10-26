from pathlib import Path
from types import MappingProxyType

from wordpaper_core.assets.local_asset_resolver import LocalAssetResolver


DEFAULT_ASSET_PATHS = MappingProxyType(
    {
        "nature.grass": "textures/nature/grass.jpg",
        "sky.clouds.soft": "textures/sky/clouds_soft.jpg",
        "sky.clouds.sparse": "textures/sky/clouds_sparse.jpg",
        "sky.clouds.fluffy": "textures/sky/clouds_fluffy.jpg",
        "sky.clouds.dense": "textures/sky/clouds_dense.jpg",
        "leather.black": "textures/leather/black.jpg",
        "leather.crocodile": "textures/leather/crocodile.jpg",
        "fur.white": "textures/fur/white.jpg",
        "fur.tiger": "textures/fur/tiger.jpg",
        "glass.frosted": "textures/glass/frosted.png",
        "glass.clear": "textures/glass/clear.png",
        "studio.liquid_chrome": "textures/studio/liquid_chrome.png",
        "studio.holographic_film": "textures/studio/holographic_film.png",
        "studio.risograph_grain": "textures/studio/risograph_grain.png",
    }
)


def create_default_asset_resolver() -> LocalAssetResolver:
    package_root = Path(__file__).resolve().parents[1]
    return LocalAssetResolver(
        root_directory=package_root / "resources",
        asset_paths=DEFAULT_ASSET_PATHS,
    )
