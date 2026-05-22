import pytest

from he_cr_model.rate_payloads import (
    AkiRatePayload,
    DuplicateRatePayloadIdError,
    MissingRatePayloadIdError,
    RatePayloadRegistry,
)


def _sample_payload(payload_id: str) -> AkiRatePayload:
    return AkiRatePayload(
        payload_id=payload_id,
        aki_s_1=1.0e7,
        review_status="verified_from_nist_asd",
    )


def test_registry_register_get_has_and_list_ids() -> None:
    registry = RatePayloadRegistry()
    payload = _sample_payload("AKI_706")
    registry.register(payload)

    assert registry.has("AKI_706") is True
    assert registry.get("AKI_706") == payload
    assert registry.list_ids() == ("AKI_706",)


def test_registry_duplicate_payload_id_fails_closed() -> None:
    registry = RatePayloadRegistry([_sample_payload("AKI_706")])
    with pytest.raises(DuplicateRatePayloadIdError, match="already registered"):
        registry.register(_sample_payload("AKI_706"))


def test_registry_missing_payload_id_raises_clear_error() -> None:
    registry = RatePayloadRegistry()
    with pytest.raises(MissingRatePayloadIdError, match="missing payload_id: AKI_587"):
        registry.get("AKI_587")
