from __future__ import annotations

from dataclasses import dataclass

from .data_loader import load_reaction_records
from .validation import is_approved_verified_status


@dataclass(frozen=True)
class Reaction:
    reaction_id: str
    equation: str
    process: str
    target_level_id: str | None
    rate: float | None
    rate_expression: str
    unit: str
    reaction_order: int
    source: str
    doi_or_url: str
    table_or_equation: str
    page_or_figure: str
    valid_range: str
    review_status: str
    enabled_by_default: bool
    notes: str

    @property
    def is_verified(self) -> bool:
        return is_approved_verified_status(self.review_status)

    @property
    def is_enabled(self) -> bool:
        return self.enabled_by_default and self.is_verified


def reaction_from_record(record: dict) -> Reaction:
    return Reaction(
        reaction_id=record["reaction_id"],
        equation=record["equation"],
        process=record["process"],
        target_level_id=record.get("target_level_id"),
        rate=record.get("rate"),
        rate_expression=record["rate_expression"],
        unit=record["unit"],
        reaction_order=int(record["reaction_order"]),
        source=record["source"],
        doi_or_url=record["doi_or_url"],
        table_or_equation=record["table_or_equation"],
        page_or_figure=record["page_or_figure"],
        valid_range=record["valid_range"],
        review_status=record["review_status"],
        enabled_by_default=bool(record["enabled_by_default"]),
        notes=record["notes"],
    )


def load_reactions() -> list[Reaction]:
    return [reaction_from_record(record) for record in load_reaction_records()]


def enabled_reactions(reactions: list[Reaction] | None = None) -> list[Reaction]:
    items = reactions if reactions is not None else load_reactions()
    return [reaction for reaction in items if reaction.is_enabled]
