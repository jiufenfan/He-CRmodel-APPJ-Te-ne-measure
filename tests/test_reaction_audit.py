from he_cr_model.data_loader import load_reaction_records
from he_cr_model.network_interfaces import ConcreteChannel, StoichTerm
from he_cr_model.reactions import Reaction, load_reactions
from he_cr_model.validation import (
    build_solver_ready_channels,
    is_approved_verified_status,
    validate_reaction_records,
)


def test_unverified_data_is_disabled_by_default() -> None:
    for reaction in load_reactions():
        if reaction.review_status != "verified_from_lee2020":
            assert not reaction.enabled_by_default
            assert not reaction.is_enabled


def test_enabled_data_is_verified() -> None:
    enabled = [reaction for reaction in load_reactions() if reaction.is_enabled]
    assert enabled
    assert all(is_approved_verified_status(reaction.review_status) for reaction in enabled)


def test_unit_validation_flags_ocr_placeholder() -> None:
    issues = validate_reaction_records(load_reaction_records())
    messages = {(issue.item_id, issue.message) for issue in issues}
    assert ("LEE2020_T1_R23_OCR_CHECK", "unit 'MISSING' inconsistent with order 2") in messages
    assert ("LEE2020_T1_R23_OCR_CHECK", "OCR check required") in messages


def test_lee_table_i_reaction_20_has_both_channels() -> None:
    records = load_reaction_records()
    reaction_20 = [record for record in records if record.get("original_reaction_no") == 20]
    equations = {record["equation"] for record in reaction_20}
    assert "He2+ + e- -> 2He" in equations
    assert "He2+ + e- -> He + He(p)" in equations
    assert all(record.get("channel_id") for record in reaction_20)
    excited = next(record for record in reaction_20 if record["equation"] == "He2+ + e- -> He + He(p)")
    assert excited["review_status"] == "needs_primary_source_check"
    assert not excited["enabled_by_default"]
def test_nist_verified_status_is_treated_as_verified() -> None:
    reaction = Reaction(
        reaction_id="TEST_NIST_RADIATION",
        equation="He(p) -> He(q) + hv",
        process="spontaneous_radiation",
        target_level_id="3_3D",
        rate=1.0,
        rate_expression="Aki",
        unit="1/s",
        reaction_order=2,
        source="synthetic",
        doi_or_url="synthetic",
        table_or_equation="synthetic",
        page_or_figure="synthetic",
        valid_range="synthetic",
        review_status="verified_from_nist_asd",
        enabled_by_default=True,
        notes="synthetic test record",
    )
    assert reaction.is_verified
    assert reaction.is_enabled


def test_network_validation_flags_unknown_species_missing_payload_and_direction() -> None:
    channel = ConcreteChannel(
        channel_id="CH_BAD",
        template_id="TPL_R3",
        family="spontaneous_radiation",
        reactants=(StoichTerm("He(3^3P)"),),
        products=(StoichTerm("He(2^3S)"),),
        directionality="lower_to_upper",
        rate_law="Aki*n_upper",
        rate_origin="tabulated",
        review_status="needs_primary_source_check",
        enabled_by_default=True,
        upper_level_energy_eV=20.0,
        lower_level_energy_eV=21.0,
        rate_payload_ref=None,
    )
    _, issues = build_solver_ready_channels(
        [channel],
        species_ids={"He(2^3S)", "e"},
        payload_ids={"PAYLOAD_1"},
    )
    messages = {issue.message for issue in issues}
    assert "unknown species_id 'He(3^3P)'" in messages
    assert "spontaneous_radiation must use directionality upper_to_lower" in messages
    assert "spontaneous_radiation requires upper_level_energy_eV > lower_level_energy_eV" in messages
    assert "missing rate_payload_ref" in messages
    assert "channel is not reviewed" in messages


def test_network_solver_ready_only_contains_reviewed_enabled_fully_bound_channels() -> None:
    good = ConcreteChannel(
        channel_id="CH_GOOD",
        template_id="TPL_R3",
        family="spontaneous_radiation",
        reactants=(StoichTerm("He(3^3P)"),),
        products=(StoichTerm("He(2^3S)"),),
        directionality="upper_to_lower",
        rate_law="Aki*n_upper",
        rate_origin="tabulated",
        review_status="verified_from_nist_asd",
        enabled_by_default=True,
        upper_level_energy_eV=21.0,
        lower_level_energy_eV=20.0,
        rate_payload_ref="PAYLOAD_A",
    )
    disabled = ConcreteChannel(**{**good.__dict__, "channel_id": "CH_DISABLED", "enabled_by_default": False})
    unreviewed = ConcreteChannel(**{**good.__dict__, "channel_id": "CH_UNREVIEWED", "review_status": "needs_primary_source_check"})
    missing_payload = ConcreteChannel(**{**good.__dict__, "channel_id": "CH_NO_PAYLOAD", "rate_payload_ref": None})

    solver_ready, issues = build_solver_ready_channels(
        [good, disabled, unreviewed, missing_payload],
        species_ids={"He(3^3P)", "He(2^3S)", "e"},
        payload_ids={"PAYLOAD_A"},
    )
    assert [channel.channel_id for channel in solver_ready] == ["CH_GOOD"]
    assert {issue.item_id for issue in issues} == {"CH_DISABLED", "CH_UNREVIEWED", "CH_NO_PAYLOAD"}
