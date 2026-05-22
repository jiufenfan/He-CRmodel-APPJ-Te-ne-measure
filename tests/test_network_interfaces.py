import json

import pytest

from he_cr_model.network_interfaces import ConcreteChannel, SpeciesRegistry, StoichTerm, is_solver_ready_channel
from he_cr_model.paths import project_root


def _load_schema(name: str) -> dict:
    path = project_root() / "schemas" / name
    return json.loads(path.read_text(encoding="utf-8"))


def test_new_network_schemas_exist_with_required_keys() -> None:
    reaction_template = _load_schema("reaction_template.schema.json")
    concrete_channel = _load_schema("concrete_channel.schema.json")
    rate_payload = _load_schema("rate_payload.schema.json")

    assert "reaction_family" in reaction_template["required"]
    assert "family" in concrete_channel["required"]
    assert "payload_type" in rate_payload["required"]


def test_species_registry_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate species_id"):
        SpeciesRegistry.from_ids(["e", "He(2^3S)", "e"])


def test_spontaneous_radiation_requires_upper_to_lower_energy_order() -> None:
    channel = ConcreteChannel(
        channel_id="CH_BAD_RAD",
        template_id="TPL_R3",
        family="spontaneous_radiation",
        reactants=(StoichTerm("He(3^3P)"),),
        products=(StoichTerm("He(2^3S)"),),
        directionality="upper_to_lower",
        rate_law="Aki*n_upper",
        rate_origin="tabulated",
        review_status="verified_from_nist_asd",
        enabled_by_default=True,
        upper_level_energy_eV=20.0,
        lower_level_energy_eV=21.0,
    )
    assert not is_solver_ready_channel(channel)
    assert "upper_level_energy_eV > lower_level_energy_eV" in " ".join(channel.validation_issues())


def test_solver_ready_channel_requires_approved_review_status_and_enabled() -> None:
    channel = ConcreteChannel(
        channel_id="CH_OK_RAD",
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
    )
    assert is_solver_ready_channel(channel)

    not_enabled = ConcreteChannel(**{**channel.__dict__, "enabled_by_default": False})
    assert not is_solver_ready_channel(not_enabled)

    not_reviewed = ConcreteChannel(**{**channel.__dict__, "review_status": "needs_primary_source_check"})
    assert not is_solver_ready_channel(not_reviewed)
