from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .data_loader import load_nist_level_records, load_nist_line_records, load_nist_staged_records
from .levels import LEVELS_N5, Level
from .ls_term_mapping import JResolvedLineRecord, JStateToLSTermMapping


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

    def state_to_ls_map(self) -> dict[str, str]:
        return {state.state_id: state.solver_level_id for state in self.states}


@dataclass(frozen=True)
class SpectroscopicLine:
    line_id: str
    upper_state_id: str
    lower_state_id: str
    wavelength_nm: float | None = None
    einstein_a_s: float | None = None
    review_status: str = "structure_only"


@dataclass(frozen=True)
class SpectroscopicLineRegistry:
    lines: tuple[SpectroscopicLine, ...]
    states: SpectroscopicStateRegistry

    @classmethod
    def from_lines(
        cls,
        lines: list[SpectroscopicLine],
        states: SpectroscopicStateRegistry,
    ) -> "SpectroscopicLineRegistry":
        return cls(lines=tuple(lines), states=states)

    def __post_init__(self) -> None:
        line_ids = [line.line_id for line in self.lines]
        if len(line_ids) != len(set(line_ids)):
            raise ValueError("duplicate spectroscopic line_id detected")

        for line in self.lines:
            self.states.get(line.upper_state_id)
            self.states.get(line.lower_state_id)

    def get(self, line_id: str) -> SpectroscopicLine:
        for line in self.lines:
            if line.line_id == line_id:
                return line
        raise KeyError(f"Unknown spectroscopic line_id: {line_id}")

    def line_to_j_state_map(self) -> dict[str, tuple[str, str]]:
        return {line.line_id: (line.upper_state_id, line.lower_state_id) for line in self.lines}

    def ls_transition_members(self) -> dict[str, tuple[str, ...]]:
        groups: dict[str, list[str]] = {}
        state_to_ls = self.states.state_to_ls_map()
        for line in self.lines:
            upper_ls = state_to_ls[line.upper_state_id]
            lower_ls = state_to_ls[line.lower_state_id]
            transition_id = f"{upper_ls}->{lower_ls}"
            groups.setdefault(transition_id, []).append(line.line_id)
        return {key: tuple(value) for key, value in groups.items()}


class MissingNistRegistryDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class NistRegistryPipelineResult:
    state_registry: SpectroscopicStateRegistry
    line_registry: SpectroscopicLineRegistry
    j_state_mappings: tuple[JStateToLSTermMapping, ...]
    j_resolved_lines: tuple[JResolvedLineRecord, ...]
    has_nist_levels_file: bool
    has_nist_lines_file: bool

    @property
    def data_available(self) -> bool:
        return self.has_nist_levels_file or self.has_nist_lines_file


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


def _read_state_id(record: dict) -> str:
    for key in ("state_id", "j_state_id", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("NIST level record missing state_id/j_state_id/id")


def _read_solver_level_id(record: dict) -> str:
    normalized = record.get("normalized")
    if isinstance(normalized, dict):
        value = normalized.get("solver_level_id")
        if isinstance(value, str) and value.strip():
            return value.strip()
    value = record.get("solver_level_id")
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError("NIST level record missing normalized.solver_level_id")


def _read_j_label(record: dict) -> str:
    for key in ("J", "j", "j_label"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("NIST level record missing J/j/j_label")


def _read_line_state_ref(record: dict, key: str) -> str:
    value = record.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise ValueError(f"NIST line record missing {key}")


def _read_line_id(record: dict) -> str:
    for key in ("line_id", "id", "transition_id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError("NIST line record missing line_id/id/transition_id")


def _read_line_state_ref_alias(record: dict, *keys: str) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    raise ValueError(f"NIST line record missing any of: {', '.join(keys)}")


def build_nist_spectroscopic_registries(
    *,
    solver_levels: SolverLevelRegistry | None = None,
) -> tuple[SpectroscopicStateRegistry, SpectroscopicLineRegistry]:
    try:
        level_records = load_nist_level_records()
        line_records = load_nist_line_records()
    except FileNotFoundError as exc:
        raise MissingNistRegistryDataError(
            "nist_hei_levels.json and nist_hei_lines.json are required for full NIST registry build"
        ) from exc

    level_registry = solver_levels or SolverLevelRegistry.from_default_n5()
    states = [
        SpectroscopicState(
            state_id=_read_state_id(record),
            solver_level_id=_read_solver_level_id(record),
            j_label=_read_j_label(record),
            energy_eV=record.get("energy_eV"),
            review_status=str(record.get("review_status", "structure_only")),
        )
        for record in level_records
    ]
    state_registry = SpectroscopicStateRegistry.from_states(states=states, solver_levels=level_registry)

    lines = [
        SpectroscopicLine(
            line_id=str(record["line_id"]),
            upper_state_id=_read_line_state_ref(record, "upper_state_id"),
            lower_state_id=_read_line_state_ref(record, "lower_state_id"),
            wavelength_nm=record.get("wavelength_nm"),
            einstein_a_s=record.get("einstein_a_s"),
            review_status=str(record.get("review_status", "structure_only")),
        )
        for record in line_records
    ]
    if states:
        line_registry = SpectroscopicLineRegistry.from_lines(lines=lines, states=state_registry)
    else:
        line_registry = SpectroscopicLineRegistry.from_lines(lines=[], states=state_registry)
    return state_registry, line_registry


def build_nist_registry_pipeline(
    *,
    solver_levels: SolverLevelRegistry | None = None,
    base_dir: Path | None = None,
) -> NistRegistryPipelineResult:
    level_registry = solver_levels or SolverLevelRegistry.from_default_n5()
    staged = load_nist_staged_records(base_dir=base_dir)

    states: list[SpectroscopicState] = []
    j_state_mappings: list[JStateToLSTermMapping] = []
    for record in staged.levels:
        state_id = _read_state_id(record)
        solver_level_id = _read_solver_level_id(record)
        review_status = str(record.get("review_status", "needs_primary_source_check"))
        enabled_by_default = bool(record.get("enabled_by_default", False))
        source = str(record.get("source", "nist_asd"))
        j_label = str(record.get("J") or record.get("j") or record.get("j_label") or "MISSING_J")
        states.append(
            SpectroscopicState(
                state_id=state_id,
                solver_level_id=solver_level_id,
                j_label=j_label,
                energy_eV=record.get("energy_eV"),
                review_status=review_status,
            )
        )
        j_state_mappings.append(
            JStateToLSTermMapping(
                j_state_id=state_id,
                ls_term_level_id=solver_level_id,
                review_status=review_status,
                enabled_by_default=enabled_by_default,
                source=source,
            )
        )

    state_registry = SpectroscopicStateRegistry.from_states(states=states, solver_levels=level_registry)

    lines: list[SpectroscopicLine] = []
    j_resolved_lines: list[JResolvedLineRecord] = []
    for record in staged.lines:
        line_id = _read_line_id(record)
        upper_state_id = _read_line_state_ref_alias(record, "upper_state_id", "upper_j_state_id")
        lower_state_id = _read_line_state_ref_alias(record, "lower_state_id", "lower_j_state_id")
        review_status = str(record.get("review_status", "needs_primary_source_check"))
        enabled_by_default = bool(record.get("enabled_by_default", False))
        source = str(record.get("source", "nist_asd"))
        einstein_a_s = record.get("einstein_a_s")
        lines.append(
            SpectroscopicLine(
                line_id=line_id,
                upper_state_id=upper_state_id,
                lower_state_id=lower_state_id,
                wavelength_nm=record.get("wavelength_nm"),
                einstein_a_s=einstein_a_s,
                review_status=review_status,
            )
        )
        j_resolved_lines.append(
            JResolvedLineRecord(
                line_id=line_id,
                upper_j_state_id=upper_state_id,
                lower_j_state_id=lower_state_id,
                einstein_a_s=einstein_a_s,
                review_status=review_status,
                enabled_by_default=enabled_by_default,
                source=source,
            )
        )

    line_registry = SpectroscopicLineRegistry.from_lines(lines=lines, states=state_registry)
    return NistRegistryPipelineResult(
        state_registry=state_registry,
        line_registry=line_registry,
        j_state_mappings=tuple(j_state_mappings),
        j_resolved_lines=tuple(j_resolved_lines),
        has_nist_levels_file=staged.has_levels_file,
        has_nist_lines_file=staged.has_lines_file,
    )
