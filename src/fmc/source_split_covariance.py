"""Source-split joint covariance readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_SOURCE_SPLIT_COVARIANCE_FIELDS = [
    "CovarianceID",
    "TargetSpace",
    "Status",
    "UsesPublicSN",
    "UsesPublicBAO",
    "IncludesSNBAOCrossCovariance",
    "CoordinateNative",
    "K1Compatible",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]


def load_source_split_covariance_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate source-split covariance registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_SOURCE_SPLIT_COVARIANCE_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"source-split covariance registry missing columns: {missing}")
    return df


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def source_split_covariance_issues(row: pd.Series) -> list[str]:
    """Return blocking issues for one covariance candidate."""
    issues: list[str] = []
    if str(row.get("Status", "")).strip().lower() != "available":
        issues.append("covariance_not_available")
    for field, issue in [
        ("UsesPublicSN", "public_sn_not_used"),
        ("UsesPublicBAO", "public_bao_not_used"),
        ("IncludesSNBAOCrossCovariance", "sn_bao_cross_covariance_missing"),
        ("CoordinateNative", "coordinate_native_false"),
        ("K1Compatible", "k1_compatible_false"),
    ]:
        if not _truthy(row.get(field, "")):
            issues.append(issue)
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(part for part in blocking.split(";") if part)
    if _truthy(row.get("AllowedForK2Scoring", "")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return list(dict.fromkeys(issues))


def source_split_covariance_allowed(row: pd.Series) -> bool:
    """Return whether a covariance candidate can be used for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "")) and not source_split_covariance_issues(row)
