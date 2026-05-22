from __future__ import annotations

from dataclasses import dataclass

from .validation import is_approved_verified_status


RADIATIVE_FAMILY = "spontaneous_radiation"


@dataclass(frozen=True)
class StoichTerm:
    species_id: str
    nu: int = 1


@dataclass(frozen=True)
class ReactionTemplate:
    template_id: str
    reaction_id: str
    reaction_family: str
    reactants: tuple[str, ...]
    products: tuple[str, ...]
    placeholders: tuple[str, ...]
    rate_payload_ref: str | None
    source_record_ref: str
    review_status: str
    enabled_by_default: bool


@dataclass(frozen=True)
class ConcreteChannel:
    channel_id: str
    template_id: str
    family: str
    reactants: tuple[StoichTerm, ...]
    products: tuple[StoichTerm, ...]
    directionality: str
    rate_law: str
    rate_origin: str
    review_status: str
    enabled_by_default: bool
    energy_order_constraint: str | None = None
    upper_level_energy_eV: float | None = None
    lower_level_energy_eV: float | None = None
    rate_payload_ref: str | None = None

    def validation_issues(self) -> list[str]:
        issues: list[str] = []
        if not self.reactants:
            issues.append("reactants must not be empty")
        if not self.products:
            issues.append("products must not be empty")

        if self.family == RADIATIVE_FAMILY:
            if self.directionality != "upper_to_lower":
                issues.append("spontaneous_radiation must use directionality upper_to_lower")
            if self.upper_level_energy_eV is None or self.lower_level_energy_eV is None:
                issues.append("spontaneous_radiation requires upper/lower level energies")
            elif self.upper_level_energy_eV <= self.lower_level_energy_eV:
                issues.append("spontaneous_radiation requires upper_level_energy_eV > lower_level_energy_eV")
        return issues


@dataclass(frozen=True)
class SpeciesRegistry:
    species_ids: tuple[str, ...]

    @classmethod
    def from_ids(cls, species_ids: list[str]) -> "SpeciesRegistry":
        deduped = list(dict.fromkeys(species_ids))
        if len(deduped) != len(species_ids):
            raise ValueError("duplicate species_id detected")
        if any(not species_id for species_id in deduped):
            raise ValueError("species_id must be non-empty")
        return cls(species_ids=tuple(deduped))


def is_solver_ready_channel(channel: ConcreteChannel) -> bool:
    if channel.validation_issues():
        return False
    if not channel.enabled_by_default:
        return False
    if not is_approved_verified_status(channel.review_status):
        return False
    return True
