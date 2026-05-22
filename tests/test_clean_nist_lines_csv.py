from __future__ import annotations

import csv
from pathlib import Path


def test_clean_nist_lines_csv_has_expected_columns() -> None:
    root = Path(__file__).resolve().parents[1]
    clean_csv = root / "data" / "staged" / "nist_hei_lines_clean.csv"
    assert clean_csv.exists()

    with clean_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames is not None

        # No reference columns.
        assert "tp_ref" not in reader.fieldnames
        assert "line_ref" not in reader.fieldnames

        # Required normalized columns.
        for name in (
            "wavelength_nm",
            "Aki",
            "aki_unit",
            "lower_conf",
            "lower_term",
            "lower_J",
            "upper_conf",
            "upper_term",
            "upper_J",
            "lower_energy_eV",
            "upper_energy_eV",
            "energy_unit",
        ):
            assert name in reader.fieldnames

        first = next(reader)
        assert first["energy_unit"] == "eV"
        assert first["aki_unit"] == "1/s"
