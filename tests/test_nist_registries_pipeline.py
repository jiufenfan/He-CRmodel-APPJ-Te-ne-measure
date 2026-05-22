from __future__ import annotations

import json

from he_cr_model.ls_term_mapping import aggregate_j_resolved_lines_to_ls_transfers
from he_cr_model.registries import (
    SolverLevelRegistry,
    build_default_species_registry,
    build_nist_registry_pipeline,
)


def _write_records(path, records) -> None:
    path.write_text(json.dumps({"records": records}, ensure_ascii=True), encoding="utf-8")


def test_nist_registry_pipeline_returns_empty_when_files_missing(tmp_path) -> None:
    result = build_nist_registry_pipeline(
        solver_levels=SolverLevelRegistry.from_default_n5(),
        base_dir=tmp_path,
    )

    assert not result.has_nist_levels_file
    assert not result.has_nist_lines_file
    assert not result.data_available
    assert result.j_state_mappings == ()
    assert result.j_resolved_lines == ()
    assert result.state_registry.states == ()
    assert result.line_registry.lines == ()


def test_nist_registry_pipeline_builds_aggregation_inputs_when_files_exist(tmp_path) -> None:
    _write_records(
        tmp_path / "nist_hei_levels.json",
        [
            {
                "state_id": "HeI_3_3D_J2",
                "J": "2",
                "normalized": {"solver_level_id": "3_3D"},
                "review_status": "verified_from_nist_asd",
                "enabled_by_default": True,
                "source": "nist_asd",
            },
            {
                "state_id": "HeI_2_3P_J1",
                "J": "1",
                "normalized": {"solver_level_id": "2_3P"},
                "review_status": "verified_from_nist_asd",
                "enabled_by_default": True,
                "source": "nist_asd",
            },
        ],
    )
    _write_records(
        tmp_path / "nist_hei_lines.json",
        [
            {
                "line_id": "NIST_L1",
                "upper_state_id": "HeI_3_3D_J2",
                "lower_state_id": "HeI_2_3P_J1",
                "einstein_a_s": 1.1e7,
                "review_status": "verified_from_nist_asd",
                "enabled_by_default": True,
                "source": "nist_asd",
            }
        ],
    )

    result = build_nist_registry_pipeline(
        solver_levels=SolverLevelRegistry.from_default_n5(),
        base_dir=tmp_path,
    )

    assert result.has_nist_levels_file
    assert result.has_nist_lines_file
    assert result.data_available
    assert len(result.j_state_mappings) == 2
    assert len(result.j_resolved_lines) == 1

    transfers, issues = aggregate_j_resolved_lines_to_ls_transfers(
        lines=list(result.j_resolved_lines),
        mappings=list(result.j_state_mappings),
    )
    assert issues == []
    assert len(transfers) == 1
    assert transfers[0].upper_ls_term_level_id == "3_3D"
    assert transfers[0].lower_ls_term_level_id == "2_3P"


def test_default_species_registry_behavior_stays_unchanged() -> None:
    registry = build_default_species_registry()
    assert registry.has("e")
    assert registry.has("hv")
    assert registry.has("He(3^3D)")
