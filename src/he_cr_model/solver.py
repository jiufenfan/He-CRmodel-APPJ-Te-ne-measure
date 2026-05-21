from __future__ import annotations

from dataclasses import dataclass
from math import exp

from .rates import ai_loss_rate_s
from .reactions import Reaction


@dataclass(frozen=True)
class PopulationResult:
    populations: dict[str, float]
    diagnostics: list[str]


def apply_enabled_ai_losses(
    seed_populations: dict[str, float],
    reactions: list[Reaction],
    neutral_density_cm3: float,
    timescale_s: float,
) -> PopulationResult:
    """Apply verified AI loss terms to seed populations.

    This is a v0.1.0 sanity helper, not a full CR matrix solver.
    The caller must provide the timescale explicitly.
    """

    populations = dict(seed_populations)
    diagnostics: list[str] = []
    for reaction in reactions:
        if not reaction.is_enabled or reaction.process != "AI" or not reaction.target_level_id:
            continue
        if reaction.target_level_id not in populations:
            continue
        loss_rate = ai_loss_rate_s(reaction, neutral_density_cm3)
        populations[reaction.target_level_id] *= exp(-loss_rate * timescale_s)
        diagnostics.append(f"applied {reaction.reaction_id}")

    for level_id, value in populations.items():
        if value < 0:
            raise ValueError(f"Negative population for {level_id}: {value}")
    return PopulationResult(populations=populations, diagnostics=diagnostics)


def fail_closed_scan_message() -> str:
    return (
        "FAIL_CLOSED: v0.1.0 does not contain verified electron-impact source terms "
        "or verified transition probabilities required for a quantitative CR scan."
    )
