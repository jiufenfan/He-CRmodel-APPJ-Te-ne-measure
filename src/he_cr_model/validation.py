from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


VALID_REVIEW_STATUSES = {
    "verified_from_lee2020",
    "needs_primary_source_check",
    "needs_digitization",
    "estimated_placeholder",
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

    if record.get("enabled_by_default") and review_status != "verified_from_lee2020":
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
