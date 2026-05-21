from he_cr_model.spectra import load_spectral_lines, missing_verified_transition_data


def test_target_spectral_line_mapping() -> None:
    lines = {line.line_id: line for line in load_spectral_lines()}
    assert set(lines) == {"HE_587_6", "HE_667_8", "HE_706_5", "HE_728_1"}
    assert lines["HE_587_6"].upper_level_id == "3_3D"
    assert lines["HE_667_8"].upper_level_id == "3_1D"
    assert lines["HE_706_5"].upper_level_id == "3_3S"
    assert lines["HE_728_1"].upper_level_id == "3_1S"


def test_missing_verified_transition_data_is_explicit() -> None:
    assert set(missing_verified_transition_data()) == {"HE_587_6", "HE_667_8", "HE_706_5", "HE_728_1"}
