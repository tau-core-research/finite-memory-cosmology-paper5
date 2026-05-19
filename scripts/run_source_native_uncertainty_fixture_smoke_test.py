#!/usr/bin/env python3
"""Smoke-test source-native backreaction bootstrap/covariance validation.

This uses artificial fixture data only. It verifies the uncertainty-export
path, not a cosmological result.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.source_native_backreaction import (
    SOURCE_NATIVE_FAMILY_IDS,
    validate_bootstrap_samples,
    validate_omega_covariance_long,
)

EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FIXTURE_OMEGA = EVIDENCE / "source_native_backreaction_fixture_omega_vector.csv"
OUT_BOOTSTRAP = EVIDENCE / "source_native_backreaction_fixture_bootstrap_samples.csv"
OUT_COV = EVIDENCE / "source_native_backreaction_fixture_covariance.csv"
OUT_AUDIT = EVIDENCE / "source_native_uncertainty_fixture_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_uncertainty_fixture_smoke_summary.csv"
OUT_DOC = DOCS / "source_native_uncertainty_fixture_smoke_test.md"


def make_bootstrap_fixture(omega: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in omega.iterrows():
        base_sample = int(row["SampleID"])
        for boot_id, jitter in enumerate([-0.02, 0.0, 0.02]):
            rows.append(
                {
                    "FamilyID": row["FamilyID"],
                    "SampleID": base_sample * 10 + boot_id,
                    "z": float(row["z"]),
                    "Omega_R_plus_3Omega_Q": float(row["Omega_R_plus_3Omega_Q"]) * (1.0 + jitter),
                    "Source": "fixture_uncertainty_smoke_test_not_observational_data",
                    "ClaimBoundary": "source_native_uncertainty_fixture_no_measurement_validation",
                }
            )
    return pd.DataFrame(rows)


def covariance_from_bootstrap(bootstrap: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for family_id, group in bootstrap.groupby("FamilyID"):
        piv = group.pivot_table(index="SampleID", columns="z", values="Omega_R_plus_3Omega_Q", aggfunc="first")
        # Drop incomplete samples to keep covariance square and finite.
        piv = piv.dropna(axis=0, how="any")
        z_values = [float(z) for z in piv.columns]
        cov = np.cov(piv.to_numpy(float), rowvar=False)
        cov = np.atleast_2d(cov)
        for i, zi in enumerate(z_values):
            for j, zj in enumerate(z_values):
                rows.append(
                    {
                        "FamilyID": family_id,
                        "z_i": zi,
                        "z_j": zj,
                        "Covariance": float(cov[i, j]),
                        "Source": "fixture_uncertainty_smoke_test_not_observational_data",
                        "ClaimBoundary": "source_native_uncertainty_fixture_no_measurement_validation",
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    if not FIXTURE_OMEGA.exists():
        raise FileNotFoundError(f"run fixture vector smoke test first: {FIXTURE_OMEGA}")
    omega = pd.read_csv(FIXTURE_OMEGA)
    bootstrap = make_bootstrap_fixture(omega)
    covariance = covariance_from_bootstrap(bootstrap)

    bootstrap_issues = validate_bootstrap_samples(bootstrap)
    covariance_issues = validate_omega_covariance_long(covariance)

    bootstrap.to_csv(OUT_BOOTSTRAP, index=False)
    covariance.to_csv(OUT_COV, index=False)
    audit = pd.DataFrame(
        [
            {
                "ObjectID": "FIXTURE_BOOTSTRAP_SAMPLES",
                "Rows": len(bootstrap),
                "Issues": ";".join(bootstrap_issues),
                "Status": "VALID" if not bootstrap_issues else "INVALID",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_uncertainty_fixture_no_measurement_validation",
            },
            {
                "ObjectID": "FIXTURE_COVARIANCE",
                "Rows": len(covariance),
                "Issues": ";".join(covariance_issues),
                "Status": "VALID" if not covariance_issues else "INVALID",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "source_native_uncertainty_fixture_no_measurement_validation",
            },
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_UNCERTAINTY_FIXTURE_SMOKE_TEST_V1",
                "FamiliesDeclared": len(SOURCE_NATIVE_FAMILY_IDS),
                "BootstrapRowsWritten": len(bootstrap),
                "CovarianceRowsWritten": len(covariance),
                "BootstrapValidationIssues": ";".join(bootstrap_issues),
                "CovarianceValidationIssues": ";".join(covariance_issues),
                "FixtureUncertaintyPipelinePasses": not bootstrap_issues and not covariance_issues,
                "FixtureDataOnly": True,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_UNCERTAINTY_FIXTURE_SMOKE_PASSED"
                if not bootstrap_issues and not covariance_issues
                else "SOURCE_NATIVE_UNCERTAINTY_FIXTURE_SMOKE_FAILED",
                "StrongestAllowedClaim": "source-native uncertainty validation code path works on artificial fixture data",
                "PrimaryResidualRisk": "fixture uncertainty is not observational uncertainty and does not replace source-native bootstrap/covariance exports",
                "NextAction": "replace fixture uncertainty with real source_native_backreaction_bootstrap_samples.csv or covariance.csv",
                "ClaimBoundary": "source_native_uncertainty_fixture_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Uncertainty Fixture Smoke Test",
                "",
                "Status: artificial fixture only; no measurement validation.",
                "",
                "This verifies that source-native bootstrap and covariance exports can be validated when provided. It does not use observational uncertainty.",
                "",
                "## Outputs",
                "",
                f"- Bootstrap fixture: `{OUT_BOOTSTRAP.relative_to(ROOT)}`",
                f"- Covariance fixture: `{OUT_COV.relative_to(ROOT)}`",
                f"- Audit: `{OUT_AUDIT.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_BOOTSTRAP}")
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
