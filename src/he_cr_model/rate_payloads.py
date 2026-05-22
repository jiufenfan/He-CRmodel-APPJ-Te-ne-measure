from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AkiRatePayload:
    payload_id: str
    aki_s_1: float
    review_status: str


@dataclass(frozen=True)
class AnalyticRatePayload:
    payload_id: str
    expression: str
    coefficients: dict[str, float]
    review_status: str


@dataclass(frozen=True)
class TabulatedRatePoint:
    te_eV: float
    k_value: float


@dataclass(frozen=True)
class TabulatedRatePayload:
    payload_id: str
    points: tuple[TabulatedRatePoint, ...]
    review_status: str


@dataclass(frozen=True)
class CrossSectionDerivedRatePlaceholder:
    payload_id: str
    source_ref: str
    review_status: str
    enabled_by_default: bool = False
