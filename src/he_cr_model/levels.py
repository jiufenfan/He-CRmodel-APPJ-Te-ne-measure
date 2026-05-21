from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    level_id: str
    n: int
    spin_multiplicity: int
    orbital: str
    label: str
    energy_eV: float | None = None
    review_status: str = "structure_only"


ORBITALS_BY_N = {
    1: ["S"],
    2: ["S", "P"],
    3: ["S", "P", "D"],
    4: ["S", "P", "D", "F"],
    5: ["S", "P", "D", "F", "G"],
}


def _level_id(n: int, spin: int, orbital: str) -> str:
    return f"{n}_{spin}{orbital}"


def build_levels(max_n: int = 5) -> list[Level]:
    if max_n < 1 or max_n > 5:
        raise ValueError("v0.1.0 supports only 1 <= max_n <= 5")

    levels: list[Level] = [Level("1_1S", 1, 1, "S", "1^1S")]
    for n in range(2, max_n + 1):
        for orbital in ORBITALS_BY_N[n]:
            for spin in (1, 3):
                label = f"{n}^{spin}{orbital}"
                levels.append(Level(_level_id(n, spin, orbital), n, spin, orbital, label))
    return levels


LEVELS_N5 = build_levels(5)


def get_level(level_id: str) -> Level:
    for level in LEVELS_N5:
        if level.level_id == level_id:
            return level
    raise KeyError(f"Unknown level_id: {level_id}")
