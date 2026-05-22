import pytest

from he_cr_model.levels import LEVELS_N5, Level
from he_cr_model.registries import (
    SolverLevelRegistry,
    SpeciesRegistry,
    SpectroscopicState,
    SpectroscopicStateRegistry,
)


def test_species_registry_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate species_id"):
        SpeciesRegistry.from_ids(["e", "He(2^3S)", "e"])


def test_solver_level_registry_uses_ls_term_levels() -> None:
    registry = SolverLevelRegistry.from_default_n5()
    assert registry.get("3_3D").label == "3^3D"
    assert len(registry.levels) == len(LEVELS_N5)


def test_solver_level_registry_rejects_duplicate_level_ids() -> None:
    levels = [Level("X", 2, 1, "S", "2^1S"), Level("X", 2, 3, "S", "2^3S")]
    with pytest.raises(ValueError, match="duplicate solver level_id"):
        SolverLevelRegistry.from_levels(levels)


def test_spectroscopic_state_registry_maps_j_resolved_state_to_ls_solver_level() -> None:
    solver_levels = SolverLevelRegistry.from_default_n5()
    states = [
        SpectroscopicState(
            state_id="HeI_3_3D_J2",
            solver_level_id="3_3D",
            j_label="2",
            review_status="structure_only",
        )
    ]
    registry = SpectroscopicStateRegistry.from_states(states=states, solver_levels=solver_levels)

    assert registry.get("HeI_3_3D_J2").solver_level_id == "3_3D"


def test_spectroscopic_state_registry_rejects_unknown_solver_level_reference() -> None:
    solver_levels = SolverLevelRegistry.from_default_n5()
    states = [
        SpectroscopicState(
            state_id="HeI_BAD_J",
            solver_level_id="3_3D_J2",
            j_label="2",
        )
    ]
    with pytest.raises(ValueError, match="unknown solver level_id"):
        SpectroscopicStateRegistry.from_states(states=states, solver_levels=solver_levels)
