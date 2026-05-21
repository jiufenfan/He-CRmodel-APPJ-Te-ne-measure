from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return project_root() / "data"


def raw_sources_dir() -> Path:
    return data_dir() / "raw_sources"


def staged_data_dir() -> Path:
    return data_dir() / "staged"


def canonical_data_dir() -> Path:
    return data_dir() / "canonical"
