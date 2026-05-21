from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class FitCandidate:
    electron_temperature_eV: float
    electron_density_cm3: float
    error: float


def line_ratio_error(observed: dict[str, float], calculated: dict[str, float]) -> float:
    terms: list[float] = []
    for ratio_id, observed_value in observed.items():
        if ratio_id not in calculated:
            raise KeyError(f"Missing calculated ratio {ratio_id}")
        calc_value = calculated[ratio_id]
        if calc_value <= 0:
            raise ValueError(f"Calculated ratio must be positive for {ratio_id}")
        terms.append(((observed_value - calc_value) / calc_value) ** 2)
    return sqrt(sum(terms))
