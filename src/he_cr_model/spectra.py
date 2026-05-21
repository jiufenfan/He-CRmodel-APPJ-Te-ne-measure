from __future__ import annotations

from dataclasses import dataclass

from .data_loader import load_spectral_line_records


@dataclass(frozen=True)
class SpectralLine:
    line_id: str
    wavelength_nm: float
    upper_level_id: str
    lower_level_id: str
    transition: str
    einstein_a_s: float | None
    review_status: str
    enabled_by_default: bool
    notes: str

    @property
    def has_verified_intensity_data(self) -> bool:
        return self.enabled_by_default and self.review_status == "verified_from_lee2020" and self.einstein_a_s is not None


def line_from_record(record: dict) -> SpectralLine:
    return SpectralLine(
        line_id=record["line_id"],
        wavelength_nm=float(record["wavelength_nm"]),
        upper_level_id=record["upper_level_id"],
        lower_level_id=record["lower_level_id"],
        transition=record["transition"],
        einstein_a_s=record.get("einstein_a_s"),
        review_status=record["review_status"],
        enabled_by_default=bool(record["enabled_by_default"]),
        notes=record["notes"],
    )


def load_spectral_lines() -> list[SpectralLine]:
    return [line_from_record(record) for record in load_spectral_line_records()]


def missing_verified_transition_data(lines: list[SpectralLine] | None = None) -> list[str]:
    items = lines if lines is not None else load_spectral_lines()
    return [line.line_id for line in items if not line.has_verified_intensity_data]


def compute_line_intensities(populations: dict[str, float], lines: list[SpectralLine]) -> dict[str, float]:
    intensities: dict[str, float] = {}
    for line in lines:
        if not line.has_verified_intensity_data:
            raise ValueError(f"Missing verified transition data for {line.line_id}")
        population = populations.get(line.upper_level_id, 0.0)
        if population < 0:
            raise ValueError(f"Negative population for {line.upper_level_id}")
        intensities[line.line_id] = population * float(line.einstein_a_s)
    return intensities
