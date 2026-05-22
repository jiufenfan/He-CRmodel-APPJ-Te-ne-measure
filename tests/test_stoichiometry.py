from __future__ import annotations

import pytest

from he_cr_model.network_interfaces import ConcreteChannel, StoichTerm
from he_cr_model.stoichiometry import UnknownSpeciesError, assemble_channel_stoichiometry


def _channel(
    channel_id: str,
    reactants: tuple[StoichTerm, ...],
    products: tuple[StoichTerm, ...],
) -> ConcreteChannel:
    return ConcreteChannel(
        channel_id=channel_id,
        template_id="T",
        family="test_family",
        reactants=reactants,
        products=products,
        directionality="forward",
        rate_law="k*n",
        rate_origin="unit_test",
        review_status="verified_from_lee2020",
        enabled_by_default=True,
    )


def test_assemble_single_radiative_channel():
    channel = _channel(
        "R03_3_3D_to_2_3P",
        reactants=(StoichTerm("He(3_3D)"),),
        products=(StoichTerm("He(2_3P)"), StoichTerm("hv")),
    )
    result = assemble_channel_stoichiometry(
        channels=[channel],
        species_order=["He(3_3D)", "He(2_3P)", "hv"],
    )
    assert result.channel_ids == ["R03_3_3D_to_2_3P"]
    assert result.species_index == {"He(3_3D)": 0, "He(2_3P)": 1, "hv": 2}
    assert result.stoichiometry_rows == [[-1, 1, 1]]


def test_assemble_ionization_channel_electron_net_plus_one():
    channel = _channel(
        "RION_He_to_Heplus",
        reactants=(StoichTerm("e"), StoichTerm("He(1_1S)")),
        products=(StoichTerm("e", 2), StoichTerm("He+")),
    )
    result = assemble_channel_stoichiometry(
        channels=[channel],
        species_order=["e", "He(1_1S)", "He+"],
    )
    assert result.stoichiometry_rows == [[1, -1, 1]]


def test_unknown_species_raises_clear_error():
    channel = _channel(
        "RBAD",
        reactants=(StoichTerm("He(2_3S)"),),
        products=(StoichTerm("He(1_1S)"),),
    )
    with pytest.raises(UnknownSpeciesError, match="unknown species_id 'He\\(2_3S\\)'"):
        assemble_channel_stoichiometry(
            channels=[channel],
            species_order=["He(1_1S)"],
        )
