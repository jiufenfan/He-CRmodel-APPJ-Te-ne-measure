from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class AkiRatePayload:
    payload_id: str
    aki_s_1: float
    review_status: str


@dataclass(frozen=True)
class AnalyticRatePayload:
    payload_id: str
    expression: str
    coefficients: dict[str, float]
    review_status: str


@dataclass(frozen=True)
class TabulatedRatePoint:
    te_eV: float
    k_value: float


@dataclass(frozen=True)
class TabulatedRatePayload:
    payload_id: str
    points: tuple[TabulatedRatePoint, ...]
    review_status: str


@dataclass(frozen=True)
class CrossSectionDerivedRatePlaceholder:
    payload_id: str
    source_ref: str
    review_status: str
    enabled_by_default: bool = False


RatePayload = (
    AkiRatePayload
    | AnalyticRatePayload
    | TabulatedRatePayload
    | CrossSectionDerivedRatePlaceholder
)


class RatePayloadRegistryError(RuntimeError):
    """Base exception for rate payload registry failures."""


class DuplicateRatePayloadIdError(RatePayloadRegistryError):
    """Raised when registering a payload_id that already exists."""


class MissingRatePayloadIdError(RatePayloadRegistryError):
    """Raised when a requested payload_id is not present in the registry."""


class RatePayloadRegistry:
    """Minimal in-memory payload registry with fail-closed lookup behavior."""

    def __init__(self, payloads: Iterable[RatePayload] | None = None) -> None:
        self._payloads: dict[str, RatePayload] = {}
        if payloads is not None:
            for payload in payloads:
                self.register(payload)

    def register(self, payload: RatePayload) -> None:
        payload_id = payload.payload_id
        if payload_id in self._payloads:
            raise DuplicateRatePayloadIdError(
                f"payload_id already registered: {payload_id}"
            )
        self._payloads[payload_id] = payload

    def has(self, payload_id: str) -> bool:
        return payload_id in self._payloads

    def get(self, payload_id: str) -> RatePayload:
        payload = self._payloads.get(payload_id)
        if payload is None:
            raise MissingRatePayloadIdError(f"missing payload_id: {payload_id}")
        return payload

    def list_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._payloads.keys()))
