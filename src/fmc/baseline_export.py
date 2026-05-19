"""Baseline-export registry checks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_BASELINE_FIELDS = [
    "BaselineExportID",
    "ProductScope",
    "Definition",
    "Status",
    "FittedInThisNote",
    "LikelihoodNative",
    "CoordinateNative",
    "AbsorbsGlobalScaleOffset",
    "AllowedForT1Preflight",
    "AllowedForMeasurementGate",
    "Risk",
    "RequiredNextCheck",
]


def load_baseline_registry(path: str | Path) -> pd.DataFrame:
    """Load the BAO baseline export registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_BASELINE_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"baseline export registry missing columns: {missing}")
    return df


def _truthy(value) -> bool:
    return str(value).lower() == "true"


def baseline_export_issues(row: pd.Series) -> list[str]:
    """Return issues that block measurement-gate eligibility."""
    issues = []
    status = str(row.get("Status", "")).lower()
    allowed = _truthy(row.get("AllowedForMeasurementGate", "false"))

    if status != "available":
        issues.append("baseline_not_available")
    if not _truthy(row.get("LikelihoodNative", "false")):
        issues.append("not_likelihood_native")
    if not _truthy(row.get("CoordinateNative", "false")):
        issues.append("not_coordinate_native")
    if _truthy(row.get("FittedInThisNote", "false")):
        issues.append("baseline_fitted_in_this_note")
    if _truthy(row.get("AbsorbsGlobalScaleOffset", "false")) and status != "required":
        issues.append("absorbs_same_data_scale_offset")
    if allowed and issues:
        issues.append("allowed_despite_blocking_issues")
    return issues


def baseline_export_allowed(row: pd.Series) -> bool:
    """Return whether a baseline export is currently measurement-gate eligible."""
    return _truthy(row.get("AllowedForMeasurementGate", "false")) and not baseline_export_issues(row)
