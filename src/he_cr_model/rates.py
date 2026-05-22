from __future__ import annotations

from dataclasses import dataclass

from .rate_payloads import (
    AkiRatePayload,
    AnalyticRatePayload,
    CrossSectionDerivedRatePlaceholder,
    TabulatedRatePayload,
)
from .reactions import Reaction


class MissingRateError(RuntimeError):
    pass


@dataclass(frozen=True)
class RateContext:
    te_eV: float | None = None
    n_upper_cm3: float | None = None


def evaluate_aki_rate(
    payload: AkiRatePayload,
    *,
    n_upper_cm3: float,
) -> float:
    if n_upper_cm3 < 0:
        raise ValueError("n_upper_cm3 must be non-negative")
    if payload.aki_s_1 < 0:
        raise ValueError("Aki must be non-negative")
    return payload.aki_s_1 * n_upper_cm3


def evaluate_analytic_rate(
    payload: AnalyticRatePayload,
    *,
    te_eV: float,
) -> float:
    if te_eV <= 0:
        raise ValueError("te_eV must be positive")

    # Minimal verified scaffold: k = a0 + a1*Te + a2*Te^2
    a0 = payload.coefficients.get("a0", 0.0)
    a1 = payload.coefficients.get("a1", 0.0)
    a2 = payload.coefficients.get("a2", 0.0)
    rate = a0 + a1 * te_eV + a2 * (te_eV**2)
    if rate < 0:
        raise ValueError("analytic rate must be non-negative")
    return rate


def evaluate_tabulated_rate(
    payload: TabulatedRatePayload,
    *,
    te_eV: float,
) -> float:
    if te_eV <= 0:
        raise ValueError("te_eV must be positive")
    if not payload.points:
        raise MissingRateError("tabulated payload has no points")

    sorted_points = sorted(payload.points, key=lambda p: p.te_eV)
    for point in sorted_points:
        if point.te_eV == te_eV:
            if point.k_value < 0:
                raise ValueError("tabulated rate must be non-negative")
            return point.k_value

    for low, high in zip(sorted_points, sorted_points[1:]):
        if low.te_eV <= te_eV <= high.te_eV:
            span = high.te_eV - low.te_eV
            if span <= 0:
                raise ValueError("tabulated te_eV points must be strictly increasing")
            frac = (te_eV - low.te_eV) / span
            interpolated = low.k_value + frac * (high.k_value - low.k_value)
            if interpolated < 0:
                raise ValueError("tabulated interpolated rate must be non-negative")
            return interpolated

    raise MissingRateError("te_eV outside tabulated payload range")


def evaluate_cross_section_placeholder(
    payload: CrossSectionDerivedRatePlaceholder,
    *,
    context: RateContext,
) -> float:
    raise MissingRateError(
        "cross-section-derived rate evaluation is disabled until reviewed integration "
        f"is approved for payload {payload.payload_id}"
    )


def evaluate_family_rate(
    family: str,
    payload: object,
    *,
    context: RateContext,
) -> float:
    if family == "spontaneous_radiation":
        if not isinstance(payload, AkiRatePayload):
            raise TypeError("spontaneous_radiation requires AkiRatePayload")
        if context.n_upper_cm3 is None:
            raise MissingRateError("n_upper_cm3 is required for spontaneous_radiation")
        return evaluate_aki_rate(payload, n_upper_cm3=context.n_upper_cm3)

    if family in {
        "electron_impact_excitation",
        "electron_impact_deexcitation",
        "electron_impact_ionization",
        "three_body_recombination",
        "radiative_recombination",
        "dissociative_recombination",
        "associative_ionization",
        "penning_like",
        "heavy_particle_quenching",
    }:
        if isinstance(payload, AnalyticRatePayload):
            if context.te_eV is None:
                raise MissingRateError("te_eV is required for analytic rate payload")
            return evaluate_analytic_rate(payload, te_eV=context.te_eV)
        if isinstance(payload, TabulatedRatePayload):
            if context.te_eV is None:
                raise MissingRateError("te_eV is required for tabulated rate payload")
            return evaluate_tabulated_rate(payload, te_eV=context.te_eV)
        if isinstance(payload, CrossSectionDerivedRatePlaceholder):
            return evaluate_cross_section_placeholder(payload, context=context)
        raise TypeError("unsupported payload type for collisional family")

    raise MissingRateError(f"unsupported reaction family: {family}")


def constant_rate(reaction: Reaction) -> float:
    if reaction.rate is None:
        raise MissingRateError(f"Reaction {reaction.reaction_id} has no verified numeric rate")
    return float(reaction.rate)


def ai_loss_rate_s(reaction: Reaction, neutral_density_cm3: float) -> float:
    if reaction.process != "AI":
        raise ValueError(f"Reaction {reaction.reaction_id} is not an AI process")
    if reaction.unit != "cm^3/s":
        raise ValueError(f"AI reaction {reaction.reaction_id} must use cm^3/s")
    return constant_rate(reaction) * neutral_density_cm3
