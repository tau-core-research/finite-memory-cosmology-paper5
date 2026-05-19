"""Locked BAO K1 response target readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_LOCKED_RESPONSE_FIELDS = [
    "ResponseTargetID",
    "TargetSpace",
    "Status",
    "BaselineBracket",
    "AmplitudeNormalization",
    "CovarianceMetric",
    "SourceResidual",
    "SameDataDerived",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]


def load_locked_response_registry(path: str | Path) -> pd.DataFrame:
    """Load locked K1 response target registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_LOCKED_RESPONSE_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"locked K1 response registry missing columns: {missing}")
    return df


def _truthy(value) -> bool:
    return str(value).lower() == "true"


def locked_response_issues(row: pd.Series) -> list[str]:
    """Return issues blocking K2 scoring."""
    issues = []
    if str(row.get("Status", "")).lower() != "available":
        issues.append("locked_response_not_available")
    for field in ["BaselineBracket", "AmplitudeNormalization", "SourceResidual"]:
        if str(row.get(field, "")).strip() == "to_be_declared":
            issues.append(f"{field.lower()}_not_declared")
    if _truthy(row.get("SameDataDerived", "false")):
        issues.append("same_data_derived")
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(item for item in blocking.split(";") if item)
    if _truthy(row.get("AllowedForK2Scoring", "false")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return issues


def locked_response_allowed(row: pd.Series) -> bool:
    """Return whether the response target is eligible for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "false")) and not locked_response_issues(row)
