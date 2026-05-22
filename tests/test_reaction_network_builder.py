import json

from he_cr_model.reaction_network_builder import build_network_from_table_i_reference, export_network_build_result


def test_table_i_reference_builds_templates_and_channels() -> None:
    result = build_network_from_table_i_reference(
        species_ids={
            "He",
            "He+",
            "He2+",
            "He2*",
            "He*",
            "hv",
            "e",
            "He(2^3S)",
            "He(2^1S)",
            "He(2^3P)",
            "He(2^1P)",
            "He(2)",
        }
    )
    assert len(result.templates) == 39
    assert len(result.network_all) == 42
    radiative_channels = [channel for channel in result.network_all if channel.family == "spontaneous_radiation"]
    assert len(radiative_channels) == 4
    assert {channel.reactants[0].species_id for channel in radiative_channels} == {"3_3D", "3_1D", "3_3S", "3_1S"}


def test_table_i_reference_solver_ready_is_fail_closed_without_reviewed_enabled_channels() -> None:
    result = build_network_from_table_i_reference(
        species_ids={"He", "He+", "He2+", "e", "hv"},
        payload_ids={"PAYLOAD_LEE2020_T1_R03_REF"},
    )
    assert result.network_solver_ready == ()
    assert result.validation_issues


def test_table_i_reference_validation_reports_unknown_placeholder_species() -> None:
    result = build_network_from_table_i_reference(
        species_ids={"He", "He+", "He2+", "e", "hv"},
    )
    messages = {issue.message for issue in result.validation_issues}
    assert "unknown species_id 'He(p)'" in messages


def test_table_i_reference_builder_uses_default_species_registry_when_not_provided() -> None:
    result = build_network_from_table_i_reference()
    assert result.templates
    assert result.network_all


def test_network_build_result_can_be_exported_to_json(tmp_path) -> None:
    result = build_network_from_table_i_reference()
    out = tmp_path / "network_export.json"
    export_network_build_result(out, result)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["metadata"]["network_all_count"] == len(result.network_all)
    assert payload["metadata"]["network_solver_ready_count"] == len(result.network_solver_ready)
    assert "network_all" in payload
    assert "validation_issues" in payload
