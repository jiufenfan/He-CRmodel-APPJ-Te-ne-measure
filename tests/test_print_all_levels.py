from __future__ import annotations

from he_cr_model.levels import LEVELS_N5


def test_print_all_project_levels() -> None:
    # This is an explicit "printout" test for human inspection in CI logs.
    # It still asserts basic sanity so it fails closed if levels are missing.
    assert LEVELS_N5

    print("level_id,n,spin,orbital,label,energy_eV,review_status")
    for level in LEVELS_N5:
        print(
            f"{level.level_id},{level.n},{level.spin_multiplicity},{level.orbital},"
            f"{level.label},{level.energy_eV},{level.review_status}"
        )

