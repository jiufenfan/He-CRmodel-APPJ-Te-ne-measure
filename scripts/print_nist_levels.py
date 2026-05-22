from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from he_cr_model.nist_asd_parser import normalize_levels_to_eV, parse_levels_csv  # noqa: E402


def main() -> int:
    path = ROOT / "data" / "raw_sources" / "nist" / "He-levels.txt"
    if not path.exists():
        raise SystemExit(f"Missing raw levels export: {path}")

    # Detect unit based on header.
    header = path.read_text(encoding="utf-8").splitlines()[0]
    unit = "eV" if "Level (eV)" in header else "cm^-1"

    rows = parse_levels_csv(path)
    levels = normalize_levels_to_eV(rows, unit)

    print("configuration,term,J,energy_eV,uncertainty_eV,reference,energy_input_unit")
    for lv in levels:
        print(
            f"{lv.configuration},{lv.term},{lv.j},"
            f"{lv.energy_eV},{lv.uncertainty_eV},{lv.reference},{lv.energy_input_unit}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

