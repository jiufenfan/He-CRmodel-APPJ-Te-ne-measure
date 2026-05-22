from __future__ import annotations

from dataclasses import dataclass

from .validation import is_approved_verified_status


@dataclass(frozen=True)
class JStateToLSTermMapping:
    j_state_id: str
    ls_term_level_id: str
    review_status: str
    enabled_by_default: bool
    source: str


@dataclass(frozen=True)
class JResolvedLineRecord:
    line_id: str
    upper_j_state_id: str
    lower_j_state_id: str
    einstein_a_s: float | None
    review_status: str
    enabled_by_default: bool
    source: str


@dataclass(frozen=True)
class AggregatedLSTransferRecord:
    transfer_id: str
    upper_ls_term_level_id: str
    lower_ls_term_level_id: str
    member_line_ids: tuple[str, ...]
    member_upper_j_state_ids: tuple[str, ...]
    member_lower_j_state_ids: tuple[str, ...]
    aggregation_method: str
    aggregated_einstein_a_s: float | None
    review_status: str
    enabled_by_default: bool
    source: str


def build_j_state_to_ls_term_map(
    mappings: list[JStateToLSTermMapping],
) -> dict[str, str]:
    mapping_dict: dict[str, str] = {}
    for item in mappings:
        if item.j_state_id in mapping_dict and mapping_dict[item.j_state_id] != item.ls_term_level_id:
            raise ValueError(f"conflicting j_state mapping for {item.j_state_id}")
        mapping_dict[item.j_state_id] = item.ls_term_level_id
    return mapping_dict


def aggregate_j_resolved_lines_to_ls_transfers(
    lines: list[JResolvedLineRecord],
    mappings: list[JStateToLSTermMapping],
    *,
    aggregation_method: str = "sum_Aki_over_member_lines",
) -> tuple[list[AggregatedLSTransferRecord], list[str]]:
    mapping_dict = build_j_state_to_ls_term_map(mappings)
    grouped: dict[tuple[str, str], list[JResolvedLineRecord]] = {}
    issues: list[str] = []

    for line in lines:
        upper_ls = mapping_dict.get(line.upper_j_state_id)
        lower_ls = mapping_dict.get(line.lower_j_state_id)
        if upper_ls is None or lower_ls is None:
            issues.append(f"missing j_state mapping for line {line.line_id}")
            continue
        grouped.setdefault((upper_ls, lower_ls), []).append(line)

    transfers: list[AggregatedLSTransferRecord] = []
    for (upper_ls, lower_ls), members in grouped.items():
        member_line_ids = tuple(line.line_id for line in members)
        member_upper_ids = tuple(line.upper_j_state_id for line in members)
        member_lower_ids = tuple(line.lower_j_state_id for line in members)
        aki_values = [line.einstein_a_s for line in members if line.einstein_a_s is not None]
        aggregated_aki = sum(aki_values) if aki_values else None

        all_reviewed = all(is_approved_verified_status(line.review_status) for line in members)
        all_enabled = all(line.enabled_by_default for line in members)
        # reviewed aggregation records are enabled only when all member records are approved and enabled
        enabled_by_default = all_reviewed and all_enabled and aggregated_aki is not None
        review_status = "verified_from_nist_asd" if all_reviewed else "needs_primary_source_check"

        transfers.append(
            AggregatedLSTransferRecord(
                transfer_id=f"LS_{upper_ls}_TO_{lower_ls}",
                upper_ls_term_level_id=upper_ls,
                lower_ls_term_level_id=lower_ls,
                member_line_ids=member_line_ids,
                member_upper_j_state_ids=member_upper_ids,
                member_lower_j_state_ids=member_lower_ids,
                aggregation_method=aggregation_method,
                aggregated_einstein_a_s=aggregated_aki,
                review_status=review_status,
                enabled_by_default=enabled_by_default,
                source="aggregated_from_j_resolved_lines",
            )
        )

    return transfers, issues
