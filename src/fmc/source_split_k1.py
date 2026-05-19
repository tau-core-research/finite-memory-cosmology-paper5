"""Source-split K1/no-memory target readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_SOURCE_SPLIT_K1_FIELDS = [
    "TargetID",
    "TargetSpace",
    "Status",
    "CoordinateNative",
    "UsesPublicSN",
    "UsesPublicBAO",
    "UsesJointCovariance",
    "AmplitudePolicy",
    "SameDataAmplitudeFit",
    "SignFamilyExported",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]


def load_source_split_k1_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate source-split K1 target registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_SOURCE_SPLIT_K1_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"source-split K1 registry missing columns: {missing}")
    return df


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def source_split_k1_issues(row: pd.Series) -> list[str]:
    """Return issues blocking K2 scoring for one K1 target candidate."""
    issues: list[str] = []
    if str(row.get("Status", "")).strip().lower() != "available":
        issues.append("k1_target_not_available")
    for field, issue in [
        ("CoordinateNative", "coordinate_native_false"),
        ("UsesPublicSN", "public_sn_not_used"),
        ("UsesPublicBAO", "public_bao_not_used"),
        ("UsesJointCovariance", "joint_covariance_not_used"),
        ("SignFamilyExported", "sign_family_not_exported"),
    ]:
        if not _truthy(row.get(field, "")):
            issues.append(issue)
    if _truthy(row.get("SameDataAmplitudeFit", "")):
        issues.append("same_data_amplitude_fit")
    if str(row.get("AmplitudePolicy", "")).strip().lower() in {"", "to_be_declared", "planned"}:
        issues.append("amplitude_policy_not_declared")
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(part for part in blocking.split(";") if part)
    if _truthy(row.get("AllowedForK2Scoring", "")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return list(dict.fromkeys(issues))


def source_split_k1_allowed(row: pd.Series) -> bool:
    """Return whether the K1 target can be used for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "")) and not source_split_k1_issues(row)
