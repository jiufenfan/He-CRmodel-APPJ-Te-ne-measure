import pytest

from he_cr_model.ls_term_mapping import (
    JResolvedLineRecord,
    JStateToLSTermMapping,
    aggregate_j_resolved_lines_to_ls_transfers,
    build_j_state_to_ls_term_map,
)


def test_build_j_state_to_ls_term_map_rejects_conflicts() -> None:
    with pytest.raises(ValueError, match="conflicting j_state mapping"):
        build_j_state_to_ls_term_map(
            [
                JStateToLSTermMapping(
                    j_state_id="HeI_3_3D_J1",
                    ls_term_level_id="3_3D",
                    review_status="verified_from_nist_asd",
                    enabled_by_default=True,
                    source="nist",
                ),
                JStateToLSTermMapping(
                    j_state_id="HeI_3_3D_J1",
                    ls_term_level_id="3_1D",
                    review_status="verified_from_nist_asd",
                    enabled_by_default=True,
                    source="nist",
                ),
            ]
        )


def test_aggregate_j_resolved_lines_to_ls_transfer_with_audit_members() -> None:
    mappings = [
        JStateToLSTermMapping("HeI_3_3D_J1", "3_3D", "verified_from_nist_asd", True, "nist"),
        JStateToLSTermMapping("HeI_3_3D_J2", "3_3D", "verified_from_nist_asd", True, "nist"),
        JStateToLSTermMapping("HeI_2_3P_J1", "2_3P", "verified_from_nist_asd", True, "nist"),
        JStateToLSTermMapping("HeI_2_3P_J2", "2_3P", "verified_from_nist_asd", True, "nist"),
    ]
    lines = [
        JResolvedLineRecord(
            line_id="NIST_L1",
            upper_j_state_id="HeI_3_3D_J1",
            lower_j_state_id="HeI_2_3P_J1",
            einstein_a_s=1.0e7,
            review_status="verified_from_nist_asd",
            enabled_by_default=True,
            source="nist",
        ),
        JResolvedLineRecord(
            line_id="NIST_L2",
            upper_j_state_id="HeI_3_3D_J2",
            lower_j_state_id="HeI_2_3P_J2",
            einstein_a_s=2.5e7,
            review_status="verified_from_nist_asd",
            enabled_by_default=True,
            source="nist",
        ),
    ]
    transfers, issues = aggregate_j_resolved_lines_to_ls_transfers(lines, mappings)
    assert not issues
    assert len(transfers) == 1
    transfer = transfers[0]
    assert transfer.transfer_id == "LS_3_3D_TO_2_3P"
    assert transfer.member_line_ids == ("NIST_L1", "NIST_L2")
    assert transfer.aggregation_method == "sum_Aki_over_member_lines"
    assert transfer.aggregated_einstein_a_s == pytest.approx(3.5e7)
    assert transfer.review_status == "verified_from_nist_asd"
    assert transfer.enabled_by_default


def test_aggregate_j_resolved_lines_fail_closed_when_member_unreviewed() -> None:
    mappings = [
        JStateToLSTermMapping("HeI_3_1S_J0", "3_1S", "verified_from_nist_asd", True, "nist"),
        JStateToLSTermMapping("HeI_2_1P_J1", "2_1P", "verified_from_nist_asd", True, "nist"),
    ]
    lines = [
        JResolvedLineRecord(
            line_id="NIST_L3",
            upper_j_state_id="HeI_3_1S_J0",
            lower_j_state_id="HeI_2_1P_J1",
            einstein_a_s=1.2e7,
            review_status="needs_primary_source_check",
            enabled_by_default=True,
            source="nist",
        )
    ]
    transfers, issues = aggregate_j_resolved_lines_to_ls_transfers(lines, mappings)
    assert not issues
    assert len(transfers) == 1
    transfer = transfers[0]
    assert transfer.review_status == "needs_primary_source_check"
    assert not transfer.enabled_by_default
