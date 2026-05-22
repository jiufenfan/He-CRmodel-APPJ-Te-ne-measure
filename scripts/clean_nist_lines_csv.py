from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from he_cr_model.nist_asd_parser import parse_lines_csv  # noqa: E402


def main() -> int:
    raw_lines = ROOT / "data" / "raw_sources" / "nist" / "He-lines.txt"
    if not raw_lines.exists():
        raise SystemExit(f"Missing raw lines export: {raw_lines}")

    out_path = ROOT / "data" / "staged" / "nist_hei_lines_clean.csv"
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = parse_lines_csv(raw_lines)

    fieldnames = [
        "wavelength_nm",
        "wavelength_source",
        "Aki",
        "aki_unit",
        "acc",
        "lower_conf",
        "lower_term",
        "lower_J",
        "upper_conf",
        "upper_term",
        "upper_J",
        "lower_energy_eV",
        "upper_energy_eV",
        "energy_unit",
    ]

    with tmp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()

        for r in rows:
            # Per NIST ASD conventions in this export: i is lower, k is upper.
            lower_conf, lower_term, lower_j = r.conf_i, r.term_i, r.j_i
            upper_conf, upper_term, upper_j = r.conf_k, r.term_k, r.j_k
            lower_e = r.ei_eV
            upper_e = r.ek_eV

            # Defensive: if energies indicate reversed ordering, swap labels too.
            if lower_e is not None and upper_e is not None and lower_e > upper_e:
                lower_conf, upper_conf = upper_conf, lower_conf
                lower_term, upper_term = upper_term, lower_term
                lower_j, upper_j = upper_j, lower_j
                lower_e, upper_e = upper_e, lower_e

            wl = r.ritz_wl_vac_nm if r.ritz_wl_vac_nm is not None else r.obs_wl_vac_nm
            wl_src = "ritz_wl_vac_nm" if r.ritz_wl_vac_nm is not None else "obs_wl_vac_nm"

            writer.writerow(
                {
                    "wavelength_nm": wl,
                    "wavelength_source": wl_src,
                    "Aki": r.aki_s_1,
                    "aki_unit": "1/s",
                    "acc": r.acc,
                    "lower_conf": lower_conf,
                    "lower_term": lower_term,
                    "lower_J": lower_j,
                    "upper_conf": upper_conf,
                    "upper_term": upper_term,
                    "upper_J": upper_j,
                    "lower_energy_eV": lower_e,
                    "upper_energy_eV": upper_e,
                    "energy_unit": "eV",
                }
            )

    try:
        # Replace target in one step; if the target is open in Excel, this will fail.
        tmp_path.replace(out_path)
    except PermissionError as exc:
        raise SystemExit(
            f"Cannot overwrite {out_path} (likely open in another program). Close it and rerun. {exc}"
        ) from exc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
