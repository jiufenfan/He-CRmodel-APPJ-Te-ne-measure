from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import canonical_data_dir, staged_data_dir


def load_json_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError(f"{path} must contain a top-level 'records' list")
    return records


def load_reaction_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    if base_dir is not None:
        roots = [base_dir]
    else:
        roots = [canonical_data_dir(), staged_data_dir()]
    records: list[dict[str, Any]] = []
    for root in roots:
        for name in ("lee2020_table_i.json", "lee2020_table_ii_ai.json"):
            path = root / name
            if path.exists():
                records.extend(load_json_records(path))
    return records


def load_spectral_line_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    return load_json_records(root / "spectral_lines_seed.json")


def load_table_i_reference_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    return load_json_records(root / "lee2020_table_i_reference.json")


def load_nist_line_records_if_present(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    nist_lines_path = root / "nist_hei_lines.json"
    if nist_lines_path.exists():
        return load_json_records(nist_lines_path)
    return []


def load_nist_hei_levels_staged_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    return load_json_records(root / "nist_hei_levels.json")


def load_nist_hei_lines_staged_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    return load_json_records(root / "nist_hei_lines.json")


def load_nist_hei_join_report_staged_records(base_dir: Path | None = None) -> list[dict[str, Any]]:
    root = base_dir or staged_data_dir()
    return load_json_records(root / "nist_hei_join_report.json")
