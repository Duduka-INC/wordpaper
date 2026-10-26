from dataclasses import dataclass

from wordpaper_core.domain.asset_ref import AssetRef
from wordpaper_core.domain.image_fit import ImageFit
from wordpaper_core.domain.operations.operation import Operation


@dataclass(frozen=True)
class ImageFillOperation(Operation):
    asset: AssetRef
    fit: ImageFit = ImageFit.COVER
