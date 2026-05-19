#!/usr/bin/env python3
"""Validate source-native backreaction uncertainty exports."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import (
    load_csv_if_exists,
    validate_bootstrap_samples,
    validate_omega_covariance_long,
)

DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

BOOTSTRAP_EXPORT = DATA / "source_native_backreaction_bootstrap_samples.csv"
COV_EXPORT = DATA / "source_native_backreaction_covariance.csv"

OUT_AUDIT = EVIDENCE / "source_native_backreaction_uncertainty_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_backreaction_uncertainty_validation_summary.csv"
OUT_DOC = DOCS / "source_native_backreaction_uncertainty_validation.md"


def status_from_issues(exists: bool, issues: list[str]) -> str:
    if not exists:
        return "MISSING"
    if issues:
        return "INVALID"
    return "VALID"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    bootstrap = load_csv_if_exists(BOOTSTRAP_EXPORT)
    covariance = load_csv_if_exists(COV_EXPORT)

    bootstrap_issues = (
        ["source_native_backreaction_bootstrap_samples_missing"]
        if bootstrap is None
        else validate_bootstrap_samples(bootstrap)
    )
    covariance_issues = (
        ["source_native_backreaction_covariance_missing"]
        if covariance is None
        else validate_omega_covariance_long(covariance)
    )

    audit = pd.DataFrame(
        [
            {
                "ObjectID": "SOURCE_NATIVE_BACKREACTION_BOOTSTRAP_SAMPLES",
                "Path": str(BOOTSTRAP_EXPORT.relative_to(ROOT)),
                "Exists": bootstrap is not None,
                "Status": status_from_issues(bootstrap is not None, bootstrap_issues),
                "Issues": ";".join(bootstrap_issues),
                "Rows": 0 if bootstrap is None else len(bootstrap),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_uncertainty_validation_no_measurement_validation",
            },
            {
                "ObjectID": "SOURCE_NATIVE_BACKREACTION_COVARIANCE",
                "Path": str(COV_EXPORT.relative_to(ROOT)),
                "Exists": covariance is not None,
                "Status": status_from_issues(covariance is not None, covariance_issues),
                "Issues": ";".join(covariance_issues),
                "Rows": 0 if covariance is None else len(covariance),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_uncertainty_validation_no_measurement_validation",
            },
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    bootstrap_valid = bool(bootstrap is not None and not bootstrap_issues)
    covariance_valid = bool(covariance is not None and not covariance_issues)
    ready = bootstrap_valid or covariance_valid
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_BACKREACTION_UNCERTAINTY_VALIDATION_V1",
                "BootstrapSamplesValid": bootstrap_valid,
                "CovarianceValid": covariance_valid,
                "AnySourceNativeUncertaintyReady": ready,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_UNCERTAINTY_READY" if ready else "SOURCE_NATIVE_UNCERTAINTY_MISSING_OR_INVALID",
                "StrongestAllowedClaim": (
                    "source-native uncertainty export is valid for covariance-aware preflight scoring"
                    if ready
                    else "source-native uncertainty validation gate is ready, but bootstrap/covariance exports are missing or invalid"
                ),
                "PrimaryResidualRisk": (
                    "source-native vector without uncertainty remains diagnostic only"
                    if not ready
                    else "uncertainty validation does not by itself authorize measurement validation"
                ),
                "NextAction": (
                    "run covariance-aware source-native bridge benchmark"
                    if ready
                    else "provide source_native_backreaction_bootstrap_samples.csv or source_native_backreaction_covariance.csv"
                ),
                "ClaimBoundary": "source_native_uncertainty_validation_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Backreaction Uncertainty Validation",
                "",
                "Status: validation gate ready; uncertainty exports currently missing unless provided.",
                "",
                "This checks source-native bootstrap samples and/or covariance for the backreaction vector. It does not authorize measurement validation.",
                "",
                "## Outputs",
                "",
                f"- Audit: `{OUT_AUDIT.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
