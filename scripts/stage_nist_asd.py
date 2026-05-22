from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from he_cr_model.nist_asd_parser import parse_levels_csv, parse_lines_csv  # noqa: E402

RAW_NIST_DIR = ROOT / "data" / "raw_sources" / "nist"
STAGED_DIR = ROOT / "data" / "staged"
CM_1_PER_EV = 8065.544005


def _write_records(path: Path, records: list[dict]) -> None:
    payload = {"records": records}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    levels_path = RAW_NIST_DIR / "He-levels.txt"
    lines_path = RAW_NIST_DIR / "He-lines.txt"
    if not levels_path.exists():
        raise SystemExit(f"Missing raw levels export: {levels_path}")
    if not lines_path.exists():
        raise SystemExit(f"Missing raw lines export: {lines_path}")

    levels = parse_levels_csv(levels_path)
    lines = parse_lines_csv(lines_path)

    # Build a lookup for join diagnostics (staged only; no inference).
    level_key_to_index: dict[tuple[str, str, str], int] = {}
    for idx, row in enumerate(levels):
        key = (row.configuration, row.term, row.j)
        level_key_to_index[key] = idx

    # Staged outputs stay disabled until human review.
    staged_levels: list[dict] = []
    for row in levels:
        staged_levels.append(
            {
                "source_kind": "nist_asd_levels_export",
                "review_status": "needs_primary_source_check",
                "enabled_by_default": False,
                "raw": asdict(row),
            }
        )

    staged_lines: list[dict] = []
    matched = 0
    ei_le_ek = 0
    ei_gt_ek = 0
    unmatched_examples: list[dict] = []
    for row in lines:
        k_i = (row.conf_i, row.term_i, row.j_i)
        k_k = (row.conf_k, row.term_k, row.j_k)
        ok = (k_i in level_key_to_index) and (k_k in level_key_to_index)
        if ok:
            matched += 1
        elif len(unmatched_examples) < 25:
            unmatched_examples.append(
                {
                    "conf_i": row.conf_i,
                    "term_i": row.term_i,
                    "j_i": row.j_i,
                    "conf_k": row.conf_k,
                    "term_k": row.term_k,
                    "j_k": row.j_k,
                    "ritz_wl_vac_nm": row.ritz_wl_vac_nm,
                    "aki_s_1": row.aki_s_1,
                }
            )
        ei_eV = row.ei_eV
        ek_eV = row.ek_eV
        if ei_eV is not None and ek_eV is not None:
            if ei_eV <= ek_eV:
                ei_le_ek += 1
            else:
                ei_gt_ek += 1

        staged_lines.append(
            {
                "source_kind": "nist_asd_lines_export",
                "review_status": "needs_primary_source_check",
                "enabled_by_default": False,
                "raw": asdict(row),
                "normalized": {
                    "ei_eV": ei_eV,
                    "ek_eV": ek_eV,
                    "lower_level_energy_eV": min(ei_eV, ek_eV) if ei_eV is not None and ek_eV is not None else None,
                    "upper_level_energy_eV": max(ei_eV, ek_eV) if ei_eV is not None and ek_eV is not None else None,
                    "energy_unit": "eV",
                    "ei_le_ek": (ei_eV <= ek_eV) if ei_eV is not None and ek_eV is not None else None,
                    "energy_input_unit": row.energy_input_unit
                },
            }
        )

    STAGED_DIR.mkdir(parents=True, exist_ok=True)
    _write_records(STAGED_DIR / "nist_hei_levels.json", staged_levels)
    _write_records(STAGED_DIR / "nist_hei_lines.json", staged_lines)
    _write_records(
        STAGED_DIR / "nist_hei_join_report.json",
        [
            {
                "levels_count": len(levels),
                "lines_count": len(lines),
                "matched_upper_lower_by_conf_term_j": matched,
                "ei_le_ek_count": ei_le_ek,
                "ei_gt_ek_count": ei_gt_ek,
                "interpretation": "for this export Ei corresponds to lower-level energy and Ek to upper-level energy",
                "energy_unit_normalized": "eV",
                "unmatched_examples": unmatched_examples,
            }
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
