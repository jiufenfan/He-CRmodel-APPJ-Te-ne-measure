from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .network_interfaces import ConcreteChannel


VALID_REVIEW_STATUSES = {
    "verified_from_lee2020",
    "verified_from_nist_asd",
    "verified_from_primary_source",
    "needs_primary_source_check",
    "needs_digitization",
    "estimated_placeholder",
}

APPROVED_VERIFIED_REVIEW_STATUSES = {
    "verified_from_lee2020",
    "verified_from_nist_asd",
    "verified_from_primary_source",
}

UNIT_BY_ORDER = {
    2: "cm^3/s",
    3: "cm^6/s",
}


@dataclass(frozen=True)
class ValidationIssue:
    item_id: str
    severity: str
    message: str


def is_approved_verified_status(review_status: str) -> bool:
    return review_status in APPROVED_VERIFIED_REVIEW_STATUSES


def validate_reaction_record(record: dict) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    item_id = str(record.get("reaction_id", "UNKNOWN"))

    required = [
        "reaction_id",
        "equation",
        "process",
        "rate_expression",
        "unit",
        "reaction_order",
        "source",
        "doi_or_url",
        "table_or_equation",
        "page_or_figure",
        "valid_range",
        "review_status",
        "enabled_by_default",
        "notes",
    ]
    for field in required:
        if field not in record or record[field] in ("", None):
            if field == "rate" and record.get("rate_expression"):
                continue
            issues.append(ValidationIssue(item_id, "error", f"missing {field}"))

    review_status = record.get("review_status")
    if review_status not in VALID_REVIEW_STATUSES:
        issues.append(ValidationIssue(item_id, "error", f"unknown review_status {review_status!r}"))

    if record.get("enabled_by_default") and not is_approved_verified_status(str(review_status)):
        issues.append(ValidationIssue(item_id, "error", "enabled unverified data"))

    table_ref = str(record.get("table_or_equation", ""))
    if table_ref.startswith("Table I reaction") and record.get("original_reaction_no") is None:
        issues.append(ValidationIssue(item_id, "error", "missing original_reaction_no for Table I reaction"))
    if table_ref.startswith("Table I reaction") and not record.get("channel_id"):
        issues.append(ValidationIssue(item_id, "error", "missing channel_id for Table I reaction channel"))

    order = record.get("reaction_order")
    expected_unit = UNIT_BY_ORDER.get(order)
    if expected_unit is None:
        issues.append(ValidationIssue(item_id, "error", f"unsupported reaction_order {order!r}"))
    elif record.get("unit") != expected_unit:
        issues.append(ValidationIssue(item_id, "error", f"unit {record.get('unit')!r} inconsistent with order {order}"))

    notes = str(record.get("notes", ""))
    if "OCR_CHECK_REQUIRED" in notes or record.get("rate_expression") == "OCR_CHECK_REQUIRED":
        issues.append(ValidationIssue(item_id, "warning", "OCR check required"))

    return issues


def validate_reaction_records(records: Iterable[dict]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for record in records:
        issues.extend(validate_reaction_record(record))
    return issues


def validate_concrete_channel(
    channel: ConcreteChannel,
    species_ids: set[str],
    payload_ids: set[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    payload_lookup = payload_ids or set()

    for message in channel.validation_issues():
        issues.append(ValidationIssue(channel.channel_id, "error", message))

    for term in channel.reactants + channel.products:
        if term.species_id not in species_ids:
            issues.append(
                ValidationIssue(
                    channel.channel_id,
                    "error",
                    f"unknown species_id {term.species_id!r}",
                )
            )

    if not channel.rate_law:
        issues.append(ValidationIssue(channel.channel_id, "error", "missing rate_law"))

    if not channel.rate_origin:
        issues.append(ValidationIssue(channel.channel_id, "error", "missing rate_origin"))

    if channel.rate_payload_ref is None:
        issues.append(ValidationIssue(channel.channel_id, "error", "missing rate_payload_ref"))
    elif payload_lookup and channel.rate_payload_ref not in payload_lookup:
        issues.append(
            ValidationIssue(
                channel.channel_id,
                "error",
                f"unknown rate_payload_ref {channel.rate_payload_ref!r}",
            )
        )

    if channel.family != "spontaneous_radiation" and "MISSING" in channel.rate_law.upper():
        issues.append(ValidationIssue(channel.channel_id, "error", "ambiguous unit in rate_law"))

    if not is_approved_verified_status(channel.review_status):
        issues.append(ValidationIssue(channel.channel_id, "error", "channel is not reviewed"))
    if not channel.enabled_by_default:
        issues.append(ValidationIssue(channel.channel_id, "error", "channel is disabled"))

    return issues


def build_solver_ready_channels(
    channels: Iterable[ConcreteChannel],
    species_ids: set[str],
    payload_ids: set[str] | None = None,
) -> tuple[list[ConcreteChannel], list[ValidationIssue]]:
    solver_ready: list[ConcreteChannel] = []
    issues: list[ValidationIssue] = []

    for channel in channels:
        channel_issues = validate_concrete_channel(channel, species_ids=species_ids, payload_ids=payload_ids)
        if channel_issues:
            issues.extend(channel_issues)
            continue
        solver_ready.append(channel)

    return solver_ready, issues
