from he_cr_model.data_loader import (
    load_nist_hei_join_report_staged_records,
    load_nist_hei_levels_staged_records,
    load_nist_hei_lines_staged_records,
    load_reaction_records,
    load_spectral_line_records,
    load_table_i_reference_records,
)
from he_cr_model.paths import canonical_data_dir, raw_sources_dir, staged_data_dir


def test_data_layer_directories_exist() -> None:
    assert raw_sources_dir().exists()
    assert staged_data_dir().exists()
    assert canonical_data_dir().exists()


def test_reaction_loader_reads_canonical_and_staged_layers() -> None:
    reaction_ids = {record["reaction_id"] for record in load_reaction_records()}
    assert "LEE2020_AI_3_1S" in reaction_ids
    assert "LEE2020_T1_R20_EXCITED_PLACEHOLDER" in reaction_ids


def test_spectral_line_loader_reads_staged_layer() -> None:
    line_ids = {record["line_id"] for record in load_spectral_line_records()}
    assert line_ids == {"HE_587_6", "HE_667_8", "HE_706_5", "HE_728_1"}


def test_lee_table_i_reference_covers_original_reaction_numbers() -> None:
    numbers = {record["original_reaction_no"] for record in load_table_i_reference_records()}
    assert numbers == set(range(1, 26))
    assert all(not record["enabled_by_default"] for record in load_table_i_reference_records())


def test_nist_staged_exports_are_present_and_disabled() -> None:
    levels = load_nist_hei_levels_staged_records()
    lines = load_nist_hei_lines_staged_records()
    report = load_nist_hei_join_report_staged_records()

    assert levels and lines and report
    assert all(not record["enabled_by_default"] for record in levels)
    assert all(not record["enabled_by_default"] for record in lines)
    assert report[0]["matched_upper_lower_by_conf_term_j"] == report[0]["lines_count"]
    assert report[0]["ei_gt_ek_count"] == 0
    assert report[0]["ei_le_ek_count"] == report[0]["lines_count"]

    first_line = lines[0]
    assert first_line["normalized"]["energy_unit"] == "eV"
    assert first_line["normalized"]["ei_eV"] is not None
    assert first_line["normalized"]["ek_eV"] is not None
    assert first_line["normalized"]["lower_level_energy_eV"] <= first_line["normalized"]["upper_level_energy_eV"]
