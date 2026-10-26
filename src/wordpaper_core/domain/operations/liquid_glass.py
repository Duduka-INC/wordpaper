from dataclasses import dataclass

from wordpaper_core.domain.operations.operation import Operation


@dataclass(frozen=True)
class LiquidGlassOperation(Operation):
    intensity: float = 1.0
    blur_radius_ratio: float = 0.004
    refraction_offset_ratio: float = 0.002
    tint_color: str = "#e8f7ff"
    tint_opacity: float = 0.16
    highlight_opacity: float = 0.78
    shadow_opacity: float = 0.24
    edge_width_ratio: float = 0.002

    def __post_init__(self) -> None:
        if not 0 <= self.intensity <= 1:
            raise ValueError("intensity must be between 0 and 1")
        if self.blur_radius_ratio < 0:
            raise ValueError("blur_radius_ratio cannot be negative")
        if self.refraction_offset_ratio < 0:
            raise ValueError("refraction_offset_ratio cannot be negative")
        if self.edge_width_ratio < 0:
            raise ValueError("edge_width_ratio cannot be negative")

        for field_name in (
            "tint_opacity",
            "highlight_opacity",
            "shadow_opacity",
        ):
            value = getattr(self, field_name)
            if not 0 <= value <= 1:
                raise ValueError(f"{field_name} must be between 0 and 1")
