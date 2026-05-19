"""Diagnostic-transform contract helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_TRANSFORM_FIELDS = [
    "TransformID",
    "InputProducts",
    "OutputTarget",
    "Status",
    "UsesPublicCovariance",
    "CoordinateNative",
    "LikelihoodNative",
    "AllowedForMeasurementGate",
    "RequiredInputs",
    "BlockingIssue",
    "NextAction",
]


def load_transform_registry(path: str | Path) -> pd.DataFrame:
    """Load the diagnostic transform registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_TRANSFORM_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"transform registry missing columns: {missing}")
    return df


def transform_contract_issues(row: pd.Series) -> list[str]:
    """Return contract issues for a registry row."""
    issues = []
    status = str(row.get("Status", "")).lower()
    allowed = str(row.get("AllowedForMeasurementGate", "")).lower() == "true"
    blocking = str(row.get("BlockingIssue", "")).strip()
    coordinate_native = str(row.get("CoordinateNative", "")).lower() == "true"
    likelihood_native = str(row.get("LikelihoodNative", "")).lower() == "true"
    uses_covariance = str(row.get("UsesPublicCovariance", "")).lower() == "true"

    if status != "available":
        issues.append("transform_not_available")
    if blocking:
        issues.append(blocking)
    if not uses_covariance:
        issues.append("public_covariance_not_used")
    if allowed and not (coordinate_native or likelihood_native):
        issues.append("allowed_without_coordinate_native_mapping")
    if allowed and blocking:
        issues.append("allowed_despite_blocking_issue")
    return issues


def transform_allowed(row: pd.Series) -> bool:
    """Return whether a transform is currently allowed for measurement scoring."""
    allowed = str(row.get("AllowedForMeasurementGate", "")).lower() == "true"
    return allowed and not transform_contract_issues(row)
