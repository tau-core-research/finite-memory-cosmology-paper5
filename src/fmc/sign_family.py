"""Sign-family export readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_SIGN_FAMILY_FIELDS = [
    "SignFamilyID",
    "TargetSpace",
    "Status",
    "UsesPublicSN",
    "UsesPublicBAO",
    "CoordinateNative",
    "ReconstructionFamilies",
    "SignStableRule",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]


def load_sign_family_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate sign-family export registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_SIGN_FAMILY_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"sign-family registry missing columns: {missing}")
    return df


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sign_family_issues(row: pd.Series) -> list[str]:
    """Return blocking issues for one sign-family export candidate."""
    issues: list[str] = []
    if str(row.get("Status", "")).strip().lower() != "available":
        issues.append("sign_family_not_available")
    for field, issue in [
        ("UsesPublicSN", "public_sn_not_used"),
        ("UsesPublicBAO", "public_bao_not_used"),
        ("CoordinateNative", "coordinate_native_false"),
    ]:
        if not _truthy(row.get(field, "")):
            issues.append(issue)
    if str(row.get("ReconstructionFamilies", "")).strip().lower() in {"", "to_be_declared", "planned"}:
        issues.append("reconstruction_families_not_declared")
    if str(row.get("SignStableRule", "")).strip().lower() in {"", "to_be_declared", "planned"}:
        issues.append("sign_stable_rule_not_declared")
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(part for part in blocking.split(";") if part)
    if _truthy(row.get("AllowedForK2Scoring", "")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return list(dict.fromkeys(issues))


def sign_family_allowed(row: pd.Series) -> bool:
    """Return whether sign-family export is allowed for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "")) and not sign_family_issues(row)
