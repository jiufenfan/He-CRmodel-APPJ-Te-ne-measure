from __future__ import annotations

from .reactions import Reaction


class MissingRateError(RuntimeError):
    pass


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
