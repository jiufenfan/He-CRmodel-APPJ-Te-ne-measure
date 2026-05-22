from __future__ import annotations

from pathlib import Path

from he_cr_model.nist_asd_parser import parse_levels_csv


def test_parse_nist_levels_export_cleans_excel_wrappers() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = root / "data" / "raw_sources" / "nist" / "He-levels.txt"
    assert raw.exists()

    # Show the raw header line for human inspection when running with -s.
    header = raw.read_text(encoding="utf-8").splitlines()[0]
    print("raw_header=" + header)

    rows = parse_levels_csv(raw)
    assert rows

    print("cleaned_preview=configuration,term,j,level_cm_1,uncertainty_cm_1,reference")
    for row in rows[:3]:
        print(
            f"{row.configuration},{row.term},{row.j},"
            f"{row.level_cm_1},{row.uncertainty_cm_1},{row.reference}"
        )

    first = rows[0]
    # These values are from the first line of the exported file and test only cleaning/parsing.
    assert first.configuration == "1s2"
    assert first.term == "1S"
    assert first.j == "0"
    assert first.level_cm_1 == 0.0
