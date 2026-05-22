from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


_EXCEL_QUOTE_RE = re.compile(r'^="(.*)"$')
_BRACKET_RE = re.compile(r"^\[(.*)\]$")
CM_1_PER_EV = 8065.544005


def _clean_cell(value: str) -> str:
    raw = value.strip()
    if raw == "":
        return ""
    # NIST ASD exports often include Excel-friendly ="..." wrappers.
    m = _EXCEL_QUOTE_RE.match(raw)
    if m:
        raw = m.group(1)
    # Strip outer quotes if any remain after csv parsing.
    if len(raw) >= 2 and raw[0] == raw[-1] == '"':
        raw = raw[1:-1]
    return raw.strip()


def _clean_bracketed_number(value: str) -> str:
    raw = _clean_cell(value)
    m = _BRACKET_RE.match(raw)
    if m:
        raw = m.group(1)
    return raw.strip()


def _to_float_or_none(value: str) -> float | None:
    raw = _clean_bracketed_number(value)
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        # Some NIST ASD exports may contain repeated header rows in the body.
        # Let callers decide whether to skip such rows; keep the failure explicit here.
        raise


@dataclass(frozen=True)
class NistLevelsRow:
    configuration: str
    term: str
    j: str
    level_cm_1: float | None
    uncertainty_cm_1: float | None
    reference: str


@dataclass(frozen=True)
class NistLevel:
    configuration: str
    term: str
    j: str
    energy_eV: float | None
    uncertainty_eV: float | None
    reference: str
    energy_input_unit: str


@dataclass(frozen=True)
class NistLinesRow:
    obs_wl_vac_nm: float | None
    ritz_wl_vac_nm: float | None
    intens: str
    aki_s_1: float | None
    acc: str
    ei_eV: float | None
    ek_eV: float | None
    energy_input_unit: str
    conf_i: str
    term_i: str
    j_i: str
    conf_k: str
    term_k: str
    j_k: str
    type_code: str
    tp_ref: str
    line_ref: str


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, str]] = []
        for row in reader:
            # DictReader may use None key for trailing commas; drop it.
            row = {str(k): (v if v is not None else "") for k, v in row.items() if k is not None}
            rows.append(row)
    return rows


def parse_levels_csv(path: Path) -> list[NistLevelsRow]:
    out: list[NistLevelsRow] = []
    for row in _read_csv_rows(path):
        if _clean_cell(row.get("Configuration", "")) == "Configuration":
            continue
        # Support both Level(cm-1) and Level(eV) exports.
        if "Level (eV)" in row:
            level_val = _to_float_or_none(row.get("Level (eV)", ""))
            unc_val = _to_float_or_none(row.get("Uncertainty (eV)", ""))
            unit = "eV"
            level_cm_1 = (level_val * CM_1_PER_EV) if level_val is not None else None
            unc_cm_1 = (unc_val * CM_1_PER_EV) if unc_val is not None else None
        else:
            level_cm_1 = _to_float_or_none(row.get("Level (cm-1)", ""))
            unc_cm_1 = _to_float_or_none(row.get("Uncertainty (cm-1)", ""))
            unit = "cm^-1"
        out.append(
            NistLevelsRow(
                configuration=_clean_cell(row.get("Configuration", "")),
                term=_clean_cell(row.get("Term", "")),
                j=_clean_cell(row.get("J", "")),
                level_cm_1=level_cm_1,
                uncertainty_cm_1=unc_cm_1,
                reference=_clean_cell(row.get("Reference", "")),
            )
        )
    return out


def normalize_levels_to_eV(rows: list[NistLevelsRow], energy_input_unit: str) -> list[NistLevel]:
    out: list[NistLevel] = []
    for r in rows:
        if r.level_cm_1 is None:
            e_eV = None
            u_eV = None
        else:
            e_eV = r.level_cm_1 / CM_1_PER_EV
            u_eV = (r.uncertainty_cm_1 / CM_1_PER_EV) if r.uncertainty_cm_1 is not None else None
        out.append(
            NistLevel(
                configuration=r.configuration,
                term=r.term,
                j=r.j,
                energy_eV=e_eV,
                uncertainty_eV=u_eV,
                reference=r.reference,
                energy_input_unit=energy_input_unit,
            )
        )
    return out


def parse_lines_csv(path: Path) -> list[NistLinesRow]:
    out: list[NistLinesRow] = []
    for row in _read_csv_rows(path):
        # Some exports include repeated header rows (e.g. air/vac variants) mid-file.
        first = _clean_cell(row.get("obs_wl_vac(nm)", ""))
        if first in ("obs_wl_vac(nm)", "obs_wl_air(nm)"):
            continue
        try:
            obs = _to_float_or_none(row.get("obs_wl_vac(nm)", ""))
            ritz = _to_float_or_none(row.get("ritz_wl_vac(nm)", ""))
            aki = _to_float_or_none(row.get("Aki(s^-1)", ""))
            if "Ei(eV)" in row and "Ek(eV)" in row:
                ei_eV = _to_float_or_none(row.get("Ei(eV)", ""))
                ek_eV = _to_float_or_none(row.get("Ek(eV)", ""))
                energy_input_unit = "eV"
            else:
                ei_cm_1 = _to_float_or_none(row.get("Ei(cm-1)", ""))
                ek_cm_1 = _to_float_or_none(row.get("Ek(cm-1)", ""))
                ei_eV = (ei_cm_1 / CM_1_PER_EV) if ei_cm_1 is not None else None
                ek_eV = (ek_cm_1 / CM_1_PER_EV) if ek_cm_1 is not None else None
                energy_input_unit = "cm^-1"
        except ValueError:
            # Fail closed on unexpected formatting, but skip known header-like junk lines.
            continue
        out.append(
            NistLinesRow(
                obs_wl_vac_nm=obs,
                ritz_wl_vac_nm=ritz,
                intens=_clean_cell(row.get("intens", "")),
                aki_s_1=aki,
                acc=_clean_cell(row.get("Acc", "")),
                ei_eV=ei_eV,
                ek_eV=ek_eV,
                energy_input_unit=energy_input_unit,
                conf_i=_clean_cell(row.get("conf_i", "")),
                term_i=_clean_cell(row.get("term_i", "")),
                j_i=_clean_cell(row.get("J_i", "")),
                conf_k=_clean_cell(row.get("conf_k", "")),
                term_k=_clean_cell(row.get("term_k", "")),
                j_k=_clean_cell(row.get("J_k", "")),
                type_code=_clean_cell(row.get("Type", "")),
                tp_ref=_clean_cell(row.get("tp_ref", "")),
                line_ref=_clean_cell(row.get("line_ref", "")),
            )
        )
    return out


def as_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    raise TypeError(f"Unsupported type: {type(obj)}")
