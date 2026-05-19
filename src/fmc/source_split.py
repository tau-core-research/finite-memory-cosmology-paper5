"""SN+BAO/source-split benchmark contract helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_SOURCE_SPLIT_FIELDS = [
    "TransformID",
    "InputProducts",
    "OutputTarget",
    "Status",
    "UsesPublicSN",
    "UsesPublicBAO",
    "UsesCovariance",
    "CoordinateNative",
    "K1TargetExported",
    "SignFamilyExported",
    "AllowedForK2Scoring",
    "BlockingIssue",
    "NextAction",
]


def load_source_split_registry(path: str | Path) -> pd.DataFrame:
    """Load and validate the source-split transform registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_SOURCE_SPLIT_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"source-split registry missing columns: {missing}")
    return df


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def source_split_issues(row: pd.Series) -> list[str]:
    """Return blocking issues for a source-split transform row."""
    issues: list[str] = []
    status = str(row.get("Status", "")).strip().lower()
    blocking = str(row.get("BlockingIssue", "")).strip()

    if status != "available":
        issues.append("transform_not_available")
    if not _truthy(row.get("UsesPublicSN", "")):
        issues.append("public_sn_not_used")
    if not _truthy(row.get("UsesPublicBAO", "")):
        issues.append("public_bao_not_used")
    if not _truthy(row.get("UsesCovariance", "")):
        issues.append("covariance_not_used")
    if not _truthy(row.get("CoordinateNative", "")):
        issues.append("coordinate_native_mapping_missing")
    if not _truthy(row.get("K1TargetExported", "")):
        issues.append("k1_target_not_exported")
    if not _truthy(row.get("SignFamilyExported", "")):
        issues.append("sign_family_not_exported")
    if blocking:
        issues.extend(part for part in blocking.split(";") if part)

    return list(dict.fromkeys(issues))


def source_split_allowed(row: pd.Series) -> bool:
    """Return whether a source-split transform can be used for K2 scoring."""
    return _truthy(row.get("AllowedForK2Scoring", "")) and not source_split_issues(row)
