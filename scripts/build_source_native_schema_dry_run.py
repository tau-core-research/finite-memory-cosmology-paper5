#!/usr/bin/env python3
"""Build a proxy dry-run in the source-native export schema.

This deliberately does not write canonical ``source_native_*`` files. It uses
the 200-bootstrap proxy route to test schema, formula, bootstrap, covariance,
and bridge-readiness mechanics while keeping source-native scoring blocked.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RECON_IN = DATA / "regularized_full_pysr_backreaction_200_reconstruction_vector.csv"
OMEGA_SAMPLES_IN = DATA / "regularized_full_pysr_backreaction_200_omega_samples.csv"
OMEGA_COV_IN = DATA / "regularized_full_pysr_backreaction_200_omega_covariance.csv"

OUT_RECON = DATA / "source_native_schema_dry_run_reconstruction_vector.csv"
OUT_META = DATA / "source_native_schema_dry_run_selection_metadata.csv"
OUT_OMEGA = DATA / "source_native_schema_dry_run_backreaction_vector.csv"
OUT_BOOTSTRAP = DATA / "source_native_schema_dry_run_backreaction_bootstrap_samples.csv"
OUT_COV = DATA / "source_native_schema_dry_run_backreaction_covariance.csv"
OUT_AUDIT = EVIDENCE / "source_native_schema_dry_run_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_schema_dry_run_summary.csv"
OUT_DOC = DOCS / "source_native_schema_dry_run.md"

CLAIM_BOUNDARY = "source_native_schema_dry_run_proxy_not_source_native_no_measurement_validation"
FAMILY_ID = "PROXY_REGULARIZED_200_NOT_SOURCE_NATIVE"

RECON_COLUMNS = [
    "FamilyID",
    "SampleID",
    "z",
    "D",
    "D_prime",
    "D_double_prime",
    "H_D",
    "H_D_prime",
    "Source",
    "SelectionRule",
    "ClaimBoundary",
]
META_COLUMNS = [
    "FamilyID",
    "DataCombination",
    "CriteriaSet",
    "Algorithm",
    "ExpressionID",
    "SelectionRule",
    "UsesPublicSN",
    "UsesPublicBAO",
    "FittedInThisNote",
    "ClaimBoundary",
]
BOOTSTRAP_COLUMNS = ["FamilyID", "SampleID", "z", "Omega_R_plus_3Omega_Q", "Source", "ClaimBoundary"]
COV_COLUMNS = ["FamilyID", "z_i", "z_j", "Covariance", "Source", "ClaimBoundary"]


def validate_columns(df: pd.DataFrame, cols: list[str]) -> list[str]:
    missing = [c for c in cols if c not in df.columns]
    return ["missing_columns:" + "|".join(missing)] if missing else []


def covariance_wide_to_long(wide: pd.DataFrame) -> pd.DataFrame:
    rows = []
    z_labels = [c for c in wide.columns if c.startswith("z_")]
    for _, row in wide.iterrows():
        zi = float(str(row["CovRow"]).replace("z_", ""))
        for col in z_labels:
            zj = float(col.replace("z_", ""))
            rows.append(
                {
                    "FamilyID": FAMILY_ID,
                    "z_i": zi,
                    "z_j": zj,
                    "Covariance": float(row[col]),
                    "Source": str(OMEGA_COV_IN.relative_to(ROOT)),
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    recon_in = pd.read_csv(RECON_IN)
    recon = recon_in[["z", "D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].copy()
    recon.insert(0, "SampleID", 0)
    recon.insert(0, "FamilyID", FAMILY_ID)
    recon["Source"] = str(RECON_IN.relative_to(ROOT))
    recon["SelectionRule"] = "proxy_schema_dry_run_from_regularized_200_no_K2_fit_no_K1_refit"
    recon["ClaimBoundary"] = CLAIM_BOUNDARY
    recon = recon[RECON_COLUMNS]
    recon.to_csv(OUT_RECON, index=False)

    meta = pd.DataFrame(
        [
            {
                "FamilyID": FAMILY_ID,
                "DataCombination": "PantheonPlus_proxy_D_and_BAO_proxy_HD",
                "CriteriaSet": "normalized_criteria3_proxy_dry_run",
                "Algorithm": "PySR_proxy_preflight_not_author_export",
                "ExpressionID": "regularized_200_proxy_family",
                "SelectionRule": "schema_dry_run_only_not_source_native",
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "FittedInThisNote": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    meta.to_csv(OUT_META, index=False)

    omega = recon[["FamilyID", "SampleID", "z", "Source", "ClaimBoundary"]].copy()
    omega["Omega_R_plus_3Omega_Q"] = omega_r_plus_3omega_q(
        recon["z"],
        recon["D"],
        recon["D_prime"],
        recon["D_double_prime"],
        recon["H_D"],
        recon["H_D_prime"],
    )
    omega = omega[["FamilyID", "SampleID", "z", "Omega_R_plus_3Omega_Q", "Source", "ClaimBoundary"]]
    omega.to_csv(OUT_OMEGA, index=False)

    samples_in = pd.read_csv(OMEGA_SAMPLES_IN)
    bootstrap = samples_in[["SampleID", "z", "Omega_R_plus_3Omega_Q"]].copy()
    bootstrap.insert(0, "FamilyID", FAMILY_ID)
    bootstrap["Source"] = str(OMEGA_SAMPLES_IN.relative_to(ROOT))
    bootstrap["ClaimBoundary"] = CLAIM_BOUNDARY
    bootstrap = bootstrap[BOOTSTRAP_COLUMNS]
    bootstrap.to_csv(OUT_BOOTSTRAP, index=False)

    cov = covariance_wide_to_long(pd.read_csv(OMEGA_COV_IN))
    cov.to_csv(OUT_COV, index=False)

    recon_issues = validate_columns(recon, RECON_COLUMNS)
    meta_issues = validate_columns(meta, META_COLUMNS)
    bootstrap_issues = validate_columns(bootstrap, BOOTSTRAP_COLUMNS)
    cov_issues = validate_columns(cov, COV_COLUMNS)

    numeric_ok = bool(
        np.isfinite(recon[["z", "D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].to_numpy(float)).all()
        and np.isfinite(omega["Omega_R_plus_3Omega_Q"].to_numpy(float)).all()
        and np.isfinite(bootstrap["Omega_R_plus_3Omega_Q"].to_numpy(float)).all()
        and np.isfinite(cov["Covariance"].to_numpy(float)).all()
    )
    cov_pivot = cov.pivot_table(index="z_i", columns="z_j", values="Covariance", aggfunc="first")
    cov_matrix = cov_pivot.to_numpy(float)
    cov_symmetric = bool(np.allclose(cov_matrix, cov_matrix.T, atol=1e-8, rtol=1e-8))
    cov_min_eig = float(np.linalg.eigvalsh(0.5 * (cov_matrix + cov_matrix.T)).min())
    omega_recomputed_match = bool(
        np.allclose(
            omega["Omega_R_plus_3Omega_Q"].to_numpy(float),
            recon_in["Omega_R_plus_3Omega_Q"].to_numpy(float),
            atol=1e-10,
            rtol=1e-10,
        )
        if "Omega_R_plus_3Omega_Q" in recon_in.columns
        else True
    )

    audit = pd.DataFrame(
        [
            {
                "ObjectID": "DRY_RUN_RECONSTRUCTION_VECTOR",
                "Path": str(OUT_RECON.relative_to(ROOT)),
                "SchemaValid": len(recon_issues) == 0,
                "Issues": ";".join(recon_issues),
                "Rows": len(recon),
                "ProxyDryRun": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ObjectID": "DRY_RUN_SELECTION_METADATA",
                "Path": str(OUT_META.relative_to(ROOT)),
                "SchemaValid": len(meta_issues) == 0,
                "Issues": ";".join(meta_issues),
                "Rows": len(meta),
                "ProxyDryRun": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ObjectID": "DRY_RUN_BOOTSTRAP_SAMPLES",
                "Path": str(OUT_BOOTSTRAP.relative_to(ROOT)),
                "SchemaValid": len(bootstrap_issues) == 0,
                "Issues": ";".join(bootstrap_issues),
                "Rows": len(bootstrap),
                "ProxyDryRun": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ObjectID": "DRY_RUN_COVARIANCE_LONG",
                "Path": str(OUT_COV.relative_to(ROOT)),
                "SchemaValid": len(cov_issues) == 0 and cov_symmetric and cov_min_eig >= -1e-8,
                "Issues": ";".join(cov_issues),
                "Rows": len(cov),
                "ProxyDryRun": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SCHEMA_DRY_RUN_V1",
                "ReconstructionRows": len(recon),
                "BootstrapRows": len(bootstrap),
                "BootstrapSamples": int(bootstrap["SampleID"].nunique()),
                "CovarianceRows": len(cov),
                "SchemaObjectsValid": int(audit["SchemaValid"].sum()),
                "SchemaObjectsTotal": int(len(audit)),
                "NumericFinite": numeric_ok,
                "CovarianceSymmetric": cov_symmetric,
                "CovarianceMinEigenvalue": cov_min_eig,
                "OmegaRecomputedMatch": omega_recomputed_match,
                "ProxyDryRun": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SOURCE_NATIVE_SCHEMA_DRY_RUN_READY_PROXY_NOT_SOURCE_NATIVE",
                "StrongestAllowedClaim": (
                    "the source-native import schema and fixed-formula mechanics are rehearsed with a 200-bootstrap proxy export"
                ),
                "PrimaryResidualRisk": (
                    "the dry-run files are not author/reproduced source-native family exports and cannot be promoted to measurement scoring"
                ),
                "NextAction": (
                    "replace dry-run proxy files with real source_native_reconstruction_vector.csv, source_native_selection_metadata.csv, and source-native uncertainty exports"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Schema Dry Run",
                "",
                "Status: SOURCE_NATIVE_SCHEMA_DRY_RUN_READY_PROXY_NOT_SOURCE_NATIVE.",
                "",
                "This dry run writes the 200-bootstrap proxy route into a source-native-like schema without using canonical source-native filenames. It tests import mechanics only.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction dry run: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Metadata dry run: `{OUT_META.relative_to(ROOT)}`",
                f"- Backreaction vector dry run: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Bootstrap dry run: `{OUT_BOOTSTRAP.relative_to(ROOT)}`",
                f"- Covariance dry run: `{OUT_COV.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "These files are explicitly proxy dry-run artifacts. They do not authorize source-native scoring or measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_AUDIT.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
