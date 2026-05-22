import pytest

from he_cr_model.spectra import compute_line_intensities, line_from_record, load_spectral_lines, missing_verified_transition_data


def test_target_spectral_line_mapping() -> None:
    lines = {line.line_id: line for line in load_spectral_lines()}
    assert set(lines) == {"HE_587_6", "HE_667_8", "HE_706_5", "HE_728_1"}
    assert lines["HE_587_6"].upper_level_id == "3_3D"
    assert lines["HE_667_8"].upper_level_id == "3_1D"
    assert lines["HE_706_5"].upper_level_id == "3_3S"
    assert lines["HE_728_1"].upper_level_id == "3_1S"


def test_missing_verified_transition_data_is_explicit() -> None:
    assert set(missing_verified_transition_data()) == {"HE_587_6", "HE_667_8", "HE_706_5", "HE_728_1"}


def test_nist_verified_line_can_compute_intensity() -> None:
    line = line_from_record(
        {
            "line_id": "TEST_LINE",
            "wavelength_nm": 587.6,
            "upper_level_id": "3_3D",
            "lower_level_id": "2_3P",
            "transition": "3^3D -> 2^3P",
            "einstein_a_s": 1.0,
            "review_status": "verified_from_nist_asd",
            "enabled_by_default": True,
            "notes": "synthetic test record",
        }
    )
    assert compute_line_intensities({"3_3D": 2.0}, [line]) == {"TEST_LINE": 2.0}


def test_unverified_line_fails_closed() -> None:
    line = line_from_record(
        {
            "line_id": "TEST_LINE",
            "wavelength_nm": 587.6,
            "upper_level_id": "3_3D",
            "lower_level_id": "2_3P",
            "transition": "3^3D -> 2^3P",
            "einstein_a_s": 1.0,
            "review_status": "needs_primary_source_check",
            "enabled_by_default": False,
            "notes": "synthetic test record",
        }
    )
    with pytest.raises(ValueError, match="Missing verified transition data"):
        compute_line_intensities({"3_3D": 2.0}, [line])
