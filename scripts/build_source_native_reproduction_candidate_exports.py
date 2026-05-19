#!/usr/bin/env python3
"""Build a criteria-set-3 reproduction-candidate export from the 200-bootstrap runs.

The output is intentionally named ``reproduction_candidate`` rather than
``source_native`` because the arXiv source packages do not expose the author
derivative vectors or covariance. This candidate is locally reproducible from
public inputs and the registered selector, but it is not an author export.
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

D_VECTOR = DATA / "d_branch_derivative_regularized_bootstrap_200_reconstruction_vector.csv"
D_SAMPLES = DATA / "d_branch_derivative_regularized_bootstrap_200_samples.csv"
H_VECTOR = DATA / "h_branch_normalized_criteria3_bootstrap_200_reconstruction_vector.csv"
H_SAMPLES = DATA / "h_branch_normalized_criteria3_bootstrap_200_samples.csv"

OUT_RECON = DATA / "source_native_reproduction_candidate_reconstruction_vector.csv"
OUT_RECON_SAMPLES = DATA / "source_native_reproduction_candidate_reconstruction_samples.csv"
OUT_META = DATA / "source_native_reproduction_candidate_selection_metadata.csv"
OUT_OMEGA = DATA / "source_native_reproduction_candidate_backreaction_vector.csv"
OUT_BOOTSTRAP = DATA / "source_native_reproduction_candidate_backreaction_bootstrap_samples.csv"
OUT_COV = DATA / "source_native_reproduction_candidate_backreaction_covariance.csv"
OUT_AUDIT = EVIDENCE / "source_native_reproduction_candidate_validation.csv"
OUT_SUMMARY = EVIDENCE / "source_native_reproduction_candidate_summary.csv"
OUT_DOC = DOCS / "source_native_reproduction_candidate_exports.md"

CLAIM_BOUNDARY = "source_native_reproduction_candidate_no_measurement_validation"
FAMILY_ID = "QR_CRITERIA_3_REPRODUCTION_CANDIDATE"


def wide_cov_to_long(samples: pd.DataFrame) -> pd.DataFrame:
    pivot = samples.pivot_table(index="SampleID", columns="z", values="Omega_R_plus_3Omega_Q", aggfunc="first")
    cov = np.cov(pivot.to_numpy(float), rowvar=False)
    rows = []
    z_values = [float(v) for v in pivot.columns]
    for i, zi in enumerate(z_values):
        for j, zj in enumerate(z_values):
            rows.append(
                {
                    "FamilyID": FAMILY_ID,
                    "z_i": zi,
                    "z_j": zj,
                    "Covariance": float(cov[i, j]),
                    "Source": "source_native_reproduction_candidate_backreaction_bootstrap_samples",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return pd.DataFrame(rows)


def finite_derivatives_ok(df: pd.DataFrame) -> bool:
    cols = ["D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]
    return bool(np.isfinite(df[cols].to_numpy(float)).all())


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    d = pd.read_csv(D_VECTOR).sort_values("z")
    h = pd.read_csv(H_VECTOR).sort_values("z")
    z = h["z"].to_numpy(float)
    recon = pd.DataFrame(
        {
            "FamilyID": FAMILY_ID,
            "SampleID": 0,
            "z": z,
            "D": np.interp(z, d["z"].to_numpy(float), d["D_median"].to_numpy(float)),
            "D_prime": np.interp(z, d["z"].to_numpy(float), d["D_prime_median"].to_numpy(float)),
            "D_double_prime": np.interp(z, d["z"].to_numpy(float), d["D_double_prime_median"].to_numpy(float)),
            "H_D": h["H_D_proxy_median"].to_numpy(float),
            "H_D_prime": h["H_D_prime_proxy_median"].to_numpy(float),
            "Source": "local_criteria3_reproduction_candidate_D_regularized_H_normalized_200",
            "SelectionRule": "registered_normalized_criteria3_plus_d_branch_derivative_regularization_no_K2_fit",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    recon.to_csv(OUT_RECON, index=False)

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

    d_samples = pd.read_csv(D_SAMPLES)
    h_samples = pd.read_csv(H_SAMPLES)
    sample_rows = []
    omega_sample_rows = []
    common = sorted(set(d_samples["BootstrapIndex"]).intersection(set(h_samples["BootstrapIndex"])))
    for sample_id in common:
        dg = d_samples[d_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
        hg = h_samples[h_samples["BootstrapIndex"].eq(sample_id)].sort_values("z")
        z_s = hg["z"].to_numpy(float)
        D_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D"].to_numpy(float))
        Dp_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D_prime"].to_numpy(float))
        Dpp_s = np.interp(z_s, dg["z"].to_numpy(float), dg["D_double_prime"].to_numpy(float))
        H_s = hg["H_D_proxy"].to_numpy(float)
        Hp_s = hg["H_D_prime_proxy"].to_numpy(float)
        omega_s = omega_r_plus_3omega_q(z_s, D_s, Dp_s, Dpp_s, H_s, Hp_s)
        for z_val, d_val, dp_val, dpp_val, h_val, hp_val, omega_val in zip(
            z_s, D_s, Dp_s, Dpp_s, H_s, Hp_s, omega_s, strict=True
        ):
            sample_rows.append(
                {
                    "FamilyID": FAMILY_ID,
                    "SampleID": int(sample_id),
                    "z": float(z_val),
                    "D": float(d_val),
                    "D_prime": float(dp_val),
                    "D_double_prime": float(dpp_val),
                    "H_D": float(h_val),
                    "H_D_prime": float(hp_val),
                    "Source": "local_criteria3_reproduction_candidate_bootstrap_200",
                    "SelectionRule": "registered_normalized_criteria3_plus_d_branch_derivative_regularization_no_K2_fit",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
            omega_sample_rows.append(
                {
                    "FamilyID": FAMILY_ID,
                    "SampleID": int(sample_id),
                    "z": float(z_val),
                    "Omega_R_plus_3Omega_Q": float(omega_val),
                    "Source": "local_criteria3_reproduction_candidate_bootstrap_200",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )

    recon_samples = pd.DataFrame(sample_rows)
    bootstrap = pd.DataFrame(omega_sample_rows)
    recon_samples.to_csv(OUT_RECON_SAMPLES, index=False)
    bootstrap.to_csv(OUT_BOOTSTRAP, index=False)

    cov = wide_cov_to_long(bootstrap)
    cov.to_csv(OUT_COV, index=False)

    meta = pd.DataFrame(
        [
            {
                "FamilyID": FAMILY_ID,
                "DataCombination": "PantheonPlus_proxy_D_and_upstream_radial_BAO_HD",
                "CriteriaSet": "criteria_set_3_reproduction_candidate",
                "Algorithm": "PySR_local_reproduction_candidate",
                "ExpressionID": "200_bootstrap_registered_selector_family",
                "SelectionRule": "normalized_criteria3_with_d_branch_derivative_regularization",
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "FittedInThisNote": False,
                "AuthorExport": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    meta.to_csv(OUT_META, index=False)

    cov_matrix = cov.pivot_table(index="z_i", columns="z_j", values="Covariance", aggfunc="first").to_numpy(float)
    cov_sym = bool(np.allclose(cov_matrix, cov_matrix.T, atol=1e-8, rtol=1e-8))
    cov_min_eig = float(np.linalg.eigvalsh(0.5 * (cov_matrix + cov_matrix.T)).min())
    audit = pd.DataFrame(
        [
            {
                "ObjectID": "REPRODUCTION_CANDIDATE_RECONSTRUCTION_VECTOR",
                "Path": str(OUT_RECON.relative_to(ROOT)),
                "Rows": len(recon),
                "Finite": finite_derivatives_ok(recon),
                "AuthorExport": False,
                "ReproductionCandidate": True,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ObjectID": "REPRODUCTION_CANDIDATE_BOOTSTRAP_SAMPLES",
                "Path": str(OUT_BOOTSTRAP.relative_to(ROOT)),
                "Rows": len(bootstrap),
                "Finite": bool(np.isfinite(bootstrap["Omega_R_plus_3Omega_Q"].to_numpy(float)).all()),
                "AuthorExport": False,
                "ReproductionCandidate": True,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
            {
                "ObjectID": "REPRODUCTION_CANDIDATE_COVARIANCE",
                "Path": str(OUT_COV.relative_to(ROOT)),
                "Rows": len(cov),
                "Finite": bool(np.isfinite(cov["Covariance"].to_numpy(float)).all()),
                "AuthorExport": False,
                "ReproductionCandidate": True,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            },
        ]
    )
    audit.to_csv(OUT_AUDIT, index=False)

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_EXPORTS_V1",
                "FamilyID": FAMILY_ID,
                "ReconstructionRows": len(recon),
                "ReconstructionSampleRows": len(recon_samples),
                "BootstrapRows": len(bootstrap),
                "BootstrapSamples": int(bootstrap["SampleID"].nunique()),
                "CovarianceRows": len(cov),
                "FiniteReconstruction": finite_derivatives_ok(recon),
                "FiniteBootstrapOmega": bool(np.isfinite(bootstrap["Omega_R_plus_3Omega_Q"].to_numpy(float)).all()),
                "CovarianceSymmetric": cov_sym,
                "CovarianceMinEigenvalue": cov_min_eig,
                "AuthorExport": False,
                "ReproductionCandidate": True,
                "SourceNativeScoringReady": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "REPRODUCTION_CANDIDATE_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE",
                "StrongestAllowedClaim": (
                    "a local criteria-set-3 reproduction candidate export is available for preflight scoring"
                ),
                "PrimaryResidualRisk": (
                    "the candidate is not the author derivative export and cannot authorize measurement validation"
                ),
                "NextAction": "score the reproduction candidate against locked K2 and keep source-native gate closed",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Reproduction Candidate Exports",
                "",
                "Status: REPRODUCTION_CANDIDATE_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE.",
                "",
                "This builds a local criteria-set-3 reproduction candidate from the 200-bootstrap D and H_D branches. It is not an author/source-native export.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction vector: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Reconstruction samples: `{OUT_RECON_SAMPLES.relative_to(ROOT)}`",
                f"- Backreaction vector: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Bootstrap samples: `{OUT_BOOTSTRAP.relative_to(ROOT)}`",
                f"- Covariance: `{OUT_COV.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "No K2 change, no K1 refit, no scale fit, and no measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_RECON.relative_to(ROOT)}")
    print(f"Wrote {OUT_BOOTSTRAP.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
