"""Skeleton utilities for future public benchmark ingestion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REQUIRED_PRODUCT_FIELDS = [
    "product_id",
    "required",
    "data_vector_path",
    "covariance_path",
    "candidate_data_url",
    "candidate_covariance_url",
    "coordinate_mapping",
    "null_comparators",
]


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load a public ingest manifest."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ModuleNotFoundError:
        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("public ingest manifest must be a mapping")
    return data


def validate_product_entry(entry: dict[str, Any]) -> list[str]:
    """Return blocking validation issues for one product entry."""
    issues = []
    for field in REQUIRED_PRODUCT_FIELDS:
        if field not in entry:
            issues.append(f"missing_{field}")
    if entry.get("required", False) and not entry.get("data_vector_path"):
        issues.append("missing_data_vector")
    if entry.get("required", False) and not entry.get("covariance_path"):
        issues.append("missing_covariance")
    if entry.get("required", False) and not entry.get("candidate_data_url"):
        issues.append("missing_candidate_data_url")
    if entry.get("required", False) and not entry.get("candidate_covariance_url"):
        issues.append("missing_candidate_covariance_url")
    if entry.get("required", False) and not entry.get("coordinate_mapping"):
        issues.append("missing_coordinate_mapping")
    if entry.get("required", False) and not entry.get("null_comparators"):
        issues.append("missing_null_comparators")
    return issues


def product_available(entry: dict[str, Any], root: Path) -> tuple[bool, bool]:
    """Return whether data vector and covariance files are available locally."""
    data_path = entry.get("data_vector_path")
    cov_path = entry.get("covariance_path")
    has_data = bool(data_path) and (root / data_path).exists()
    has_cov = bool(cov_path) and (root / cov_path).exists()
    return has_data, has_cov


def load_bao_mean(path: str | Path) -> pd.DataFrame:
    """Load a Cobaya-style BAO mean vector."""
    return pd.read_csv(
        path,
        sep=r"\s+",
        comment="#",
        names=["z", "value", "quantity"],
        engine="python",
    )


def load_square_covariance(path: str | Path) -> np.ndarray:
    """Load a plain square covariance matrix."""
    cov = np.loadtxt(path)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1]:
        raise ValueError(f"covariance matrix is not square: {path}")
    return cov


def load_pantheon_table(path: str | Path) -> pd.DataFrame:
    """Load the Pantheon+SH0ES distance table."""
    return pd.read_csv(path, sep=r"\s+", engine="python")


def load_flat_covariance_with_size(path: str | Path) -> np.ndarray:
    """Load covariance stored as N followed by N*N scalar values."""
    values = np.loadtxt(path)
    if values.ndim != 1 or len(values) < 2:
        raise ValueError(f"flat covariance file is malformed: {path}")
    declared = int(values[0])
    flat = values[1:]
    if len(flat) != declared * declared:
        raise ValueError(
            f"flat covariance length mismatch for {path}: "
            f"declared={declared}, values={len(flat)}"
        )
    return flat.reshape((declared, declared))
