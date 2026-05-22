from __future__ import annotations

from dataclasses import dataclass

from .network_interfaces import ConcreteChannel


@dataclass(frozen=True)
class StoichiometryAssemblyResult:
    species_index: dict[str, int]
    stoichiometry_rows: list[list[int]]
    channel_ids: list[str]


class UnknownSpeciesError(ValueError):
    pass


def build_species_index(species_order: list[str]) -> dict[str, int]:
    index: dict[str, int] = {}
    for i, species_id in enumerate(species_order):
        if not species_id:
            raise ValueError("species_order contains empty species_id")
        if species_id in index:
            raise ValueError(f"species_order contains duplicate species_id: {species_id}")
        index[species_id] = i
    return index


def assemble_channel_stoichiometry(
    channels: list[ConcreteChannel],
    species_order: list[str],
) -> StoichiometryAssemblyResult:
    species_index = build_species_index(species_order)
    n_species = len(species_order)

    stoichiometry_rows: list[list[int]] = []
    channel_ids: list[str] = []

    for channel in channels:
        row = [0] * n_species

        for term in channel.reactants:
            idx = species_index.get(term.species_id)
            if idx is None:
                raise UnknownSpeciesError(
                    f"unknown species_id '{term.species_id}' in reactants for channel '{channel.channel_id}'"
                )
            row[idx] -= term.nu

        for term in channel.products:
            idx = species_index.get(term.species_id)
            if idx is None:
                raise UnknownSpeciesError(
                    f"unknown species_id '{term.species_id}' in products for channel '{channel.channel_id}'"
                )
            row[idx] += term.nu

        stoichiometry_rows.append(row)
        channel_ids.append(channel.channel_id)

    return StoichiometryAssemblyResult(
        species_index=species_index,
        stoichiometry_rows=stoichiometry_rows,
        channel_ids=channel_ids,
    )
