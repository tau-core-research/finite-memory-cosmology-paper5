"""BAO K1 response readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_K1_RESPONSE_FIELDS = [
    "ResponseID",
    "TargetSpace",
    "Definition",
    "Status",
    "SourceBaseline",
    "CoordinateNative",
    "LikelihoodNative",
    "FittedInThisNote",
    "AllowedForK2Scoring",
    "Risk",
    "RequiredNextCheck",
]


def load_k1_response_registry(path: str | Path) -> pd.DataFrame:
    """Load the BAO K1 response registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_K1_RESPONSE_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"K1 response registry missing columns: {missing}")
    return df


def _truthy(value) -> bool:
    return str(value).lower() == "true"


def k1_response_issues(row: pd.Series) -> list[str]:
    """Return issues that block K2 scoring eligibility."""
    issues = []
    if str(row.get("Status", "")).lower() != "available":
        issues.append("response_not_available")
    if not _truthy(row.get("CoordinateNative", "false")):
        issues.append("not_coordinate_native")
    if not _truthy(row.get("LikelihoodNative", "false")):
        issues.append("not_likelihood_native")
    if _truthy(row.get("FittedInThisNote", "false")):
        issues.append("response_fitted_in_this_note")
    if "same-data" in str(row.get("Risk", "")).lower():
        issues.append("same_data_response_risk")
    if _truthy(row.get("AllowedForK2Scoring", "false")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return issues


def k1_response_allowed(row: pd.Series) -> bool:
    """Return whether the response can be used for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "false")) and not k1_response_issues(row)
