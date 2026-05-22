import pytest

from he_cr_model.rate_payloads import (
    AkiRatePayload,
    AnalyticRatePayload,
    CrossSectionDerivedRatePlaceholder,
    TabulatedRatePayload,
    TabulatedRatePoint,
)
from he_cr_model.rates import MissingRateError, RateContext, evaluate_family_rate


def test_spontaneous_radiation_aki_rate() -> None:
    payload = AkiRatePayload(
        payload_id="AKI_HE_706_5",
        aki_s_1=1.0e7,
        review_status="verified_from_nist_asd",
    )
    rate = evaluate_family_rate(
        "spontaneous_radiation",
        payload,
        context=RateContext(n_upper_cm3=2.0e10),
    )
    assert rate == pytest.approx(2.0e17)


def test_analytic_rate_payload() -> None:
    payload = AnalyticRatePayload(
        payload_id="AN_EI_EXC",
        expression="a0 + a1*Te + a2*Te^2",
        coefficients={"a0": 1.0, "a1": 2.0, "a2": 0.5},
        review_status="verified_from_lee2020",
    )
    rate = evaluate_family_rate(
        "electron_impact_excitation",
        payload,
        context=RateContext(te_eV=2.0),
    )
    assert rate == pytest.approx(7.0)


def test_tabulated_rate_payload_linear_interpolation() -> None:
    payload = TabulatedRatePayload(
        payload_id="TAB_EI_ION",
        points=(
            TabulatedRatePoint(te_eV=1.0, k_value=1.0e-10),
            TabulatedRatePoint(te_eV=3.0, k_value=5.0e-10),
        ),
        review_status="verified_from_primary_source",
    )
    rate = evaluate_family_rate(
        "electron_impact_ionization",
        payload,
        context=RateContext(te_eV=2.0),
    )
    assert rate == pytest.approx(3.0e-10)


def test_cross_section_derived_rate_is_fail_closed() -> None:
    payload = CrossSectionDerivedRatePlaceholder(
        payload_id="XS_EI_EXC",
        source_ref="TODO_SOURCE",
        review_status="needs_primary_source_check",
    )
    with pytest.raises(MissingRateError, match="disabled until reviewed integration"):
        evaluate_family_rate(
            "electron_impact_excitation",
            payload,
            context=RateContext(te_eV=3.0),
        )


def test_spontaneous_radiation_requires_upper_population() -> None:
    payload = AkiRatePayload(
        payload_id="AKI_HE_587_6",
        aki_s_1=2.0e7,
        review_status="verified_from_nist_asd",
    )
    with pytest.raises(MissingRateError, match="n_upper_cm3 is required"):
        evaluate_family_rate(
            "spontaneous_radiation",
            payload,
            context=RateContext(),
        )
