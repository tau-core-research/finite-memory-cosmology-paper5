"""Readiness checks for likelihood-native baseline sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_SOURCE_FIELDS = [
    "SourceID",
    "SourceType",
    "ProductScope",
    "Definition",
    "Status",
    "HasPublicDataVector",
    "HasPublicCovariance",
    "HasBaselinePrediction",
    "HasFrozenCosmology",
    "HasReproducibleEvaluator",
    "AllowedForBaselineExport",
    "BlockingIssue",
    "NextAction",
]


def load_likelihood_baseline_sources(path: str | Path) -> pd.DataFrame:
    """Load the likelihood-native baseline source registry."""
    df = pd.read_csv(path)
    missing = [field for field in REQUIRED_SOURCE_FIELDS if field not in df.columns]
    if missing:
        raise ValueError(f"baseline source registry missing columns: {missing}")
    return df


def _truthy(value) -> bool:
    return str(value).lower() == "true"


def likelihood_source_issues(row: pd.Series) -> list[str]:
    """Return issues that block baseline export readiness."""
    issues = []
    if str(row.get("Status", "")).lower() not in {"available", "required"}:
        issues.append("source_not_available")
    if not _truthy(row.get("HasPublicDataVector", "false")):
        issues.append("missing_public_data_vector")
    if not _truthy(row.get("HasPublicCovariance", "false")):
        issues.append("missing_public_covariance")
    if not _truthy(row.get("HasBaselinePrediction", "false")):
        issues.append("missing_baseline_prediction")
    if not _truthy(row.get("HasFrozenCosmology", "false")):
        issues.append("missing_frozen_cosmology")
    if not _truthy(row.get("HasReproducibleEvaluator", "false")):
        issues.append("missing_reproducible_evaluator")
    blocking = str(row.get("BlockingIssue", "")).strip()
    if blocking:
        issues.extend(item for item in blocking.split(";") if item)
    if _truthy(row.get("AllowedForBaselineExport", "false")) and issues:
        issues.append("allowed_despite_blocking_issues")
    return issues


def likelihood_source_allowed(row: pd.Series) -> bool:
    """Return whether a source is currently eligible for baseline export."""
    return _truthy(row.get("AllowedForBaselineExport", "false")) and not likelihood_source_issues(row)
