import json

from he_cr_model.ls_term_mapping import JResolvedLineRecord, JStateToLSTermMapping
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


def test_builder_prefers_j_resolved_aggregation_when_mapping_inputs_provided() -> None:
    mappings = [
        JStateToLSTermMapping("HeI_3_3D_J1", "3_3D", "verified_from_nist_asd", True, "nist"),
        JStateToLSTermMapping("HeI_2_3P_J1", "2_3P", "verified_from_nist_asd", True, "nist"),
    ]
    lines = [
        JResolvedLineRecord(
            line_id="NIST_SYNTH_1",
            upper_j_state_id="HeI_3_3D_J1",
            lower_j_state_id="HeI_2_3P_J1",
            einstein_a_s=1.0e7,
            review_status="verified_from_nist_asd",
            enabled_by_default=True,
            source="nist",
        )
    ]
    result = build_network_from_table_i_reference(
        j_resolved_lines=lines,
        j_state_mappings=mappings,
        payload_ids={"Aki_LS_3_3D_TO_2_3P"},
    )
    radiative_channels = [channel for channel in result.network_all if channel.family == "spontaneous_radiation"]
    assert len(radiative_channels) == 1
    assert radiative_channels[0].rate_origin == "j_resolved_aggregated_to_ls_term"
    assert radiative_channels[0].reactants[0].species_id == "3_3D"
    assert radiative_channels[0].products[0].species_id == "2_3P"


def test_builder_records_aggregation_warnings_for_unmapped_j_states() -> None:
    mappings = [JStateToLSTermMapping("HeI_2_3P_J1", "2_3P", "verified_from_nist_asd", True, "nist")]
    lines = [
        JResolvedLineRecord(
            line_id="NIST_SYNTH_MISSING",
            upper_j_state_id="HeI_3_3D_J1",
            lower_j_state_id="HeI_2_3P_J1",
            einstein_a_s=1.0e7,
            review_status="verified_from_nist_asd",
            enabled_by_default=True,
            source="nist",
        )
    ]
    result = build_network_from_table_i_reference(
        j_resolved_lines=lines,
        j_state_mappings=mappings,
    )
    warning_messages = [issue.message for issue in result.validation_issues if issue.severity == "warning"]
    assert any("missing j_state mapping" in message for message in warning_messages)
