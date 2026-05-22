from __future__ import annotations

from dataclasses import dataclass

from .levels import LEVELS_N5, Level


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

    def has(self, species_id: str) -> bool:
        return species_id in self.species_ids


@dataclass(frozen=True)
class SolverLevelRegistry:
    levels: tuple[Level, ...]

    @classmethod
    def from_levels(cls, levels: list[Level]) -> "SolverLevelRegistry":
        return cls(levels=tuple(levels))

    @classmethod
    def from_default_n5(cls) -> "SolverLevelRegistry":
        return cls.from_levels(LEVELS_N5)

    def __post_init__(self) -> None:
        level_ids = [level.level_id for level in self.levels]
        if len(level_ids) != len(set(level_ids)):
            raise ValueError("duplicate solver level_id detected")

    def get(self, level_id: str) -> Level:
        for level in self.levels:
            if level.level_id == level_id:
                return level
        raise KeyError(f"Unknown solver level_id: {level_id}")

    def has(self, level_id: str) -> bool:
        return any(level.level_id == level_id for level in self.levels)


@dataclass(frozen=True)
class SpectroscopicState:
    state_id: str
    solver_level_id: str
    j_label: str
    energy_eV: float | None = None
    review_status: str = "structure_only"


@dataclass(frozen=True)
class SpectroscopicStateRegistry:
    states: tuple[SpectroscopicState, ...]
    solver_levels: SolverLevelRegistry

    @classmethod
    def from_states(
        cls,
        states: list[SpectroscopicState],
        solver_levels: SolverLevelRegistry,
    ) -> "SpectroscopicStateRegistry":
        return cls(states=tuple(states), solver_levels=solver_levels)

    def __post_init__(self) -> None:
        state_ids = [state.state_id for state in self.states]
        if len(state_ids) != len(set(state_ids)):
            raise ValueError("duplicate spectroscopic state_id detected")

        for state in self.states:
            if not self.solver_levels.has(state.solver_level_id):
                raise ValueError(
                    "spectroscopic state references unknown solver level_id: "
                    f"{state.solver_level_id}"
                )

    def get(self, state_id: str) -> SpectroscopicState:
        for state in self.states:
            if state.state_id == state_id:
                return state
        raise KeyError(f"Unknown spectroscopic state_id: {state_id}")


def build_default_species_registry() -> SpeciesRegistry:
    solver_levels = SolverLevelRegistry.from_default_n5()
    species: list[str] = [
        "e",
        "hv",
        "He",
        "He+",
        "He2+",
        "He2*",
        "He*",
        "He(2)",
    ]
    for level in solver_levels.levels:
        species.append(level.level_id)
        species.append(f"He({level.label})")
    return SpeciesRegistry.from_ids(species)
