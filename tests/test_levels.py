from he_cr_model.levels import LEVELS_N5


def test_n5_ls_term_level_count() -> None:
    assert len(LEVELS_N5) == 29


def test_expected_target_levels_exist() -> None:
    level_ids = {level.level_id for level in LEVELS_N5}
    assert {"3_1S", "3_3S", "3_1D", "3_3D", "2_1P", "2_3P"} <= level_ids
