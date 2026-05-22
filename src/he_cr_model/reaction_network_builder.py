from __future__ import annotations

import re
from dataclasses import dataclass

from .data_loader import load_nist_line_records_if_present, load_spectral_line_records, load_table_i_reference_records
from .network_interfaces import ConcreteChannel, ReactionTemplate, StoichTerm
from .validation import ValidationIssue, build_solver_ready_channels


_TOKEN_PATTERN = re.compile(r"^\s*(?:(\d+)\s*)?(.+?)\s*$")
_PLACEHOLDER_PATTERN = re.compile(r"\([pq]\)")


@dataclass(frozen=True)
class NetworkBuildResult:
    templates: tuple[ReactionTemplate, ...]
    network_all: tuple[ConcreteChannel, ...]
    network_solver_ready: tuple[ConcreteChannel, ...]
    validation_issues: tuple[ValidationIssue, ...]


def _normalize_species(raw: str) -> str:
    species = raw.strip()
    species = species.replace("e-", "e").replace("e+", "e")
    if species == "2e":
        return "e"
    if species == "2He":
        return "He"
    if species == "3He":
        return "He"
    return species


def _parse_side_tokens(side: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for part in side.split("+"):
        chunk = part.strip()
        if not chunk:
            continue
        match = _TOKEN_PATTERN.match(chunk)
        if not match:
            tokens.append((1, _normalize_species(chunk)))
            continue
        nu = int(match.group(1)) if match.group(1) else 1
        species = _normalize_species(match.group(2))
        tokens.append((nu, species))
    return tokens


def _split_equation(equation: str) -> tuple[str, str]:
    if "->" in equation:
        left, right = equation.split("->", 1)
        return left.strip(), right.strip()
    if "<->" in equation:
        left, right = equation.split("<->", 1)
        return left.strip(), right.strip()
    raise ValueError(f"unsupported equation form: {equation!r}")


def _infer_reaction_family(process: str) -> str:
    mapping = {
        "spontaneous_radiation": "spontaneous_radiation",
        "electron_impact_excitation_deexcitation": "electron_impact_excitation",
        "electron_impact_ionization": "electron_impact_ionization",
        "three_body_recombination": "three_body_recombination",
        "radiative_recombination": "radiative_recombination",
        "DR": "dissociative_recombination",
        "AI": "associative_ionization",
    }
    return mapping.get(process, "unknown_or_composite")


def _template_from_record(record: dict) -> ReactionTemplate:
    left, right = _split_equation(str(record["equation"]))
    reactants = tuple(species for _, species in _parse_side_tokens(left))
    products = tuple(species for _, species in _parse_side_tokens(right))
    placeholders = tuple(
        sorted(
            {
                species
                for species in reactants + products
                if _PLACEHOLDER_PATTERN.search(species)
            }
        )
    )

    rate_expression = str(record.get("rate_expression", ""))
    payload_ref: str | None = f"PAYLOAD_{record['reaction_id']}"
    if any(marker in rate_expression for marker in ("MISSING", "OCR_CHECK_REQUIRED", "Table II")):
        payload_ref = None

    return ReactionTemplate(
        template_id=f"{record['reaction_id']}_TPL",
        reaction_id=str(record["reaction_id"]),
        reaction_family=_infer_reaction_family(str(record["process"])),
        reactants=reactants,
        products=products,
        placeholders=placeholders,
        rate_payload_ref=payload_ref,
        source_record_ref=str(record["reaction_id"]),
        review_status=str(record["review_status"]),
        enabled_by_default=bool(record["enabled_by_default"]),
    )


def _channel_from_template(template: ReactionTemplate, equation: str) -> ConcreteChannel:
    left, right = _split_equation(equation)
    reactants = tuple(StoichTerm(species_id=species, nu=nu) for nu, species in _parse_side_tokens(left))
    products = tuple(StoichTerm(species_id=species, nu=nu) for nu, species in _parse_side_tokens(right))
    direction = "forward_only"
    if template.reaction_family == "spontaneous_radiation":
        direction = "upper_to_lower"

    return ConcreteChannel(
        channel_id=f"{template.reaction_id}_CH",
        template_id=template.template_id,
        family=template.reaction_family,
        reactants=reactants,
        products=products,
        directionality=direction,
        rate_law="MISSING" if template.rate_payload_ref is None else "payload_bound",
        rate_origin="source_table_i_reference",
        review_status=template.review_status,
        enabled_by_default=template.enabled_by_default,
        rate_payload_ref=template.rate_payload_ref,
    )


def _extract_nist_energies(line_record: dict) -> tuple[float | None, float | None]:
    normalized = line_record.get("normalized")
    if isinstance(normalized, dict):
        upper = normalized.get("upper_level_energy_eV")
        lower = normalized.get("lower_level_energy_eV")
        if isinstance(upper, (int, float)) and isinstance(lower, (int, float)):
            return float(upper), float(lower)
    return None, None


def _expand_spontaneous_radiation_from_lines(template: ReactionTemplate) -> list[ConcreteChannel]:
    line_records = load_nist_line_records_if_present()
    using_nist_lines = bool(line_records)
    if not using_nist_lines:
        line_records = load_spectral_line_records()

    expanded: list[ConcreteChannel] = []
    for line in line_records:
        upper_id = str(line.get("upper_level_id", "")).strip()
        lower_id = str(line.get("lower_level_id", "")).strip()
        if not upper_id or not lower_id:
            continue

        upper_energy, lower_energy = _extract_nist_energies(line)
        rate_payload_ref: str | None = None
        if line.get("einstein_a_s") not in (None, ""):
            rate_payload_ref = f"Aki_{line.get('line_id', 'UNKNOWN')}"

        expanded.append(
            ConcreteChannel(
                channel_id=f"{template.reaction_id}_{line.get('line_id', 'LINE')}",
                template_id=template.template_id,
                family="spontaneous_radiation",
                reactants=(StoichTerm(species_id=upper_id, nu=1),),
                products=(StoichTerm(species_id=lower_id, nu=1), StoichTerm(species_id="hv", nu=1)),
                directionality="upper_to_lower",
                rate_law="Aki*n_upper" if rate_payload_ref else "MISSING",
                rate_origin="nist_lines" if using_nist_lines else "spectral_lines_seed",
                review_status=str(line.get("review_status", template.review_status)),
                enabled_by_default=bool(line.get("enabled_by_default", False)),
                upper_level_energy_eV=upper_energy,
                lower_level_energy_eV=lower_energy,
                rate_payload_ref=rate_payload_ref,
            )
        )
    return expanded


def build_network_from_table_i_reference(
    *,
    species_ids: set[str],
    payload_ids: set[str] | None = None,
) -> NetworkBuildResult:
    records = load_table_i_reference_records()
    templates = tuple(_template_from_record(record) for record in records)
    channels_list: list[ConcreteChannel] = []
    for template, record in zip(templates, records):
        if template.reaction_family == "spontaneous_radiation":
            channels_list.extend(_expand_spontaneous_radiation_from_lines(template))
            continue
        channels_list.append(_channel_from_template(template, str(record["equation"])))
    channels = tuple(channels_list)
    solver_ready, issues = build_solver_ready_channels(channels, species_ids=species_ids, payload_ids=payload_ids)
    return NetworkBuildResult(
        templates=templates,
        network_all=channels,
        network_solver_ready=tuple(solver_ready),
        validation_issues=tuple(issues),
    )
