"""K2 scoring protocol readiness helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_K2_PROTOCOL_FIELDS = [
    "ProtocolID",
    "Target",
    "Status",
    "BaselineBracket",
    "RequiredNulls",
    "LockedOperator",
    "RhoPolicy",
    "CovariancePolicy",
    "SupportiveCondition",
    "WeakeningCondition",
    "StrongNegativeCondition",
    "NextAction",
]


def load_k2_protocol_registry(path: str | Path) -> pd.DataFrame:
    """Load the BAO K2 protocol registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_K2_PROTOCOL_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"K2 protocol registry missing columns: {missing}")
    return df


def k2_protocol_issues(row: pd.Series) -> list[str]:
    """Return issues that block K2 scoring."""
    issues = []
    if str(row.get("Status", "")).lower() != "ready":
        issues.append("protocol_not_ready")
    if "rho<=4" not in str(row.get("RhoPolicy", "")):
        issues.append("rho_bound_not_declared")
    if "p=3" not in str(row.get("LockedOperator", "")):
        issues.append("locked_kernel_not_declared")
    if "same residual covariance" not in str(row.get("CovariancePolicy", "")):
        issues.append("shared_covariance_policy_not_declared")
    if not str(row.get("RequiredNulls", "")).strip():
        issues.append("required_nulls_missing")
    if not str(row.get("BaselineBracket", "")).strip():
        issues.append("baseline_bracket_missing")
    return issues


def k2_protocol_ready(row: pd.Series) -> bool:
    """Return whether a protocol is ready for K2 scoring."""
    return not k2_protocol_issues(row)
