#!/usr/bin/env python3
"""Build surrogate backreaction-family exports from public training inputs.

This is a pipeline rehearsal for the source-native backreaction route. It uses
fixed weighted-polynomial families as stand-ins for the missing author/source
symbolic-regression exports. It must not be interpreted as source-native
measurement evidence.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q
from fmc.source_native_backreaction import SOURCE_NATIVE_FAMILY_IDS

ROOT = Path(__file__).resolve().parents[1]
BR = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SN_INPUT = BR / "source_native_training_sn_distance_proxy.csv"
BAO_INPUT = BR / "source_native_training_bao_hd_proxy.csv"

OUT_RECON = BR / "source_native_surrogate_reconstruction_vector.csv"
OUT_META = BR / "source_native_surrogate_selection_metadata.csv"
OUT_OMEGA = BR / "source_native_surrogate_backreaction_vector.csv"
OUT_COV = BR / "source_native_surrogate_backreaction_family_covariance.csv"
OUT_SUMMARY = EVIDENCE / "source_native_surrogate_family_export_summary.csv"
OUT_DOC = DOCS / "source_native_surrogate_family_exports.md"

CLAIM_BOUNDARY = "source_native_surrogate_family_exports_no_measurement_validation"

FAMILY_DEGREES = {
    "QR_CRITERIA_1": (3, 2),
    "QR_CRITERIA_2": (4, 2),
    "QR_CRITERIA_3": (5, 3),
    "QR_DESI": (5, 4),
    "QR_EBOSS": (6, 3),
}


def weighted_polyfit(x: np.ndarray, y: np.ndarray, sigma: np.ndarray, degree: int) -> np.poly1d:
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
    if int(mask.sum()) <= degree:
        raise ValueError(f"not enough finite points for degree {degree}: {int(mask.sum())}")
    return np.poly1d(np.polyfit(x[mask], y[mask], degree, w=1.0 / sigma[mask]))


def weighted_mean_by_z(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for z_value, group in df.groupby("z", sort=True):
        y = group["Hrs_over_c_proxy"].to_numpy(float)
        sigma = group["Hrs_over_c_sigma_proxy"].to_numpy(float)
        mask = np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
        if not mask.any():
            continue
        weights = 1.0 / (sigma[mask] ** 2)
        rows.append(
            {
                "z": float(z_value),
                "Hrs_over_c_proxy": float(np.sum(weights * y[mask]) / np.sum(weights)),
                "Hrs_over_c_sigma_proxy": float(np.sqrt(1.0 / np.sum(weights))),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    BR.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    sn = pd.read_csv(SN_INPUT)
    bao = weighted_mean_by_z(pd.read_csv(BAO_INPUT))

    sn_z = sn["z"].to_numpy(float)
    sn_d = sn["D_proxy_Mpc"].to_numpy(float)
    sn_sigma = sn["D_proxy_sigma_diag_Mpc"].to_numpy(float)
    bao_z = bao["z"].to_numpy(float)
    bao_h = bao["Hrs_over_c_proxy"].to_numpy(float)
    bao_sigma = bao["Hrs_over_c_sigma_proxy"].to_numpy(float)

    z_min = max(float(np.nanmin(bao_z)), float(np.nanmin(sn_z)))
    z_max = min(float(np.nanmax(bao_z)), float(np.nanmax(sn_z)))
    grid = np.linspace(z_min, z_max, 24)

    recon_rows = []
    meta_rows = []
    omega_rows = []

    for family_id in SOURCE_NATIVE_FAMILY_IDS:
        d_degree, h_degree = FAMILY_DEGREES[family_id]
        d_poly = weighted_polyfit(sn_z, sn_d, sn_sigma, d_degree)
        h_poly = weighted_polyfit(bao_z, bao_h, bao_sigma, h_degree)
        d_prime = np.polyder(d_poly, 1)
        d_double_prime = np.polyder(d_poly, 2)
        h_prime = np.polyder(h_poly, 1)

        d_val = d_poly(grid)
        dp_val = d_prime(grid)
        dpp_val = d_double_prime(grid)
        h_val = h_poly(grid)
        hp_val = h_prime(grid)
        omega = omega_r_plus_3omega_q(grid, d_val, dp_val, dpp_val, h_val, hp_val)

        selection_rule = f"surrogate_fixed_weighted_poly_D{d_degree}_HD{h_degree}_no_K2_fit"
        for z_value, d, dp, dpp, hd, hdp, omega_value in zip(
            grid, d_val, dp_val, dpp_val, h_val, hp_val, omega, strict=True
        ):
            recon_rows.append(
                {
                    "FamilyID": family_id,
                    "SampleID": 0,
                    "z": float(z_value),
                    "D": float(d),
                    "D_prime": float(dp),
                    "D_double_prime": float(dpp),
                    "H_D": float(hd),
                    "H_D_prime": float(hdp),
                    "Source": "public_SN_BAO_training_inputs_surrogate_family_export",
                    "SelectionRule": selection_rule,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
            omega_rows.append(
                {
                    "FamilyID": family_id,
                    "SampleID": 0,
                    "z": float(z_value),
                    "Omega_R_plus_3Omega_Q": float(omega_value),
                    "Source": "source_native_surrogate_reconstruction_vector",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
        meta_rows.append(
            {
                "FamilyID": family_id,
                "DataCombination": "public_SN_proxy_plus_public_BAO_HD_proxy",
                "CriteriaSet": f"surrogate_degree_pair_D{d_degree}_HD{h_degree}",
                "Algorithm": "fixed_weighted_polynomial_surrogate",
                "ExpressionID": f"POLY_D{d_degree}_HD{h_degree}",
                "SelectionRule": selection_rule,
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "FittedInThisNote": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )

    recon = pd.DataFrame(recon_rows)
    meta = pd.DataFrame(meta_rows)
    omega_df = pd.DataFrame(omega_rows)
    recon.to_csv(OUT_RECON, index=False)
    meta.to_csv(OUT_META, index=False)
    omega_df.to_csv(OUT_OMEGA, index=False)

    pivot = omega_df.pivot_table(index="FamilyID", columns="z", values="Omega_R_plus_3Omega_Q", aggfunc="first")
    cov = np.cov(pivot.to_numpy(float), rowvar=False)
    cov_rows = []
    cov_z = [float(v) for v in pivot.columns]
    for i, zi in enumerate(cov_z):
        for j, zj in enumerate(cov_z):
            cov_rows.append(
                {
                    "z_i": zi,
                    "z_j": zj,
                    "Covariance": float(cov[i, j]),
                    "Source": "surrogate_family_scatter_not_source_native_covariance",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(cov_rows).to_csv(OUT_COV, index=False)

    finite = bool(np.isfinite(recon[["D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].to_numpy()).all())
    omega_finite = bool(np.isfinite(omega_df["Omega_R_plus_3Omega_Q"].to_numpy(float)).all())
    eig_min = float(np.linalg.eigvalsh(0.5 * (cov + cov.T)).min())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_SURROGATE_FAMILY_EXPORT_V1",
                "Families": omega_df["FamilyID"].nunique(),
                "GridRowsPerFamily": int(omega_df.groupby("FamilyID")["z"].nunique().min()),
                "ReconstructionRows": len(recon),
                "OmegaRows": len(omega_df),
                "FiniteDerivativeVectors": finite,
                "FiniteOmegaVectors": omega_finite,
                "SurrogateFamilyScatterCovarianceEigenMin": eig_min,
                "SurrogateFamilyExportsReady": finite and omega_finite,
                "SourceNativeExportsReady": False,
                "SourceNativeCovarianceReady": False,
                "K2FitPerformed": False,
                "K1RefitPerformed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "SURROGATE_FAMILY_EXPORT_READY_SOURCE_NATIVE_STILL_MISSING",
                "StrongestAllowedClaim": (
                    "a surrogate multi-family backreaction export can rehearse the source-native scoring pipeline"
                ),
                "PrimaryResidualRisk": (
                    "fixed polynomial surrogate families are not the published/source-native symbolic-regression families"
                ),
                "NextAction": "score surrogate family vectors against locked K2, then replace with source-native exports when available",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Surrogate Family Exports",
                "",
                "Status: surrogate family export ready; source-native export still missing.",
                "",
                "This artifact rehearses the final backreaction route with five fixed public-input polynomial families. It deliberately does not overwrite the canonical `source_native_reconstruction_vector.csv` file and must not be used as measurement evidence.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction vector: `{OUT_RECON.relative_to(ROOT)}`",
                f"- Metadata: `{OUT_META.relative_to(ROOT)}`",
                f"- Backreaction vector: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Family-scatter covariance: `{OUT_COV.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_RECON}")
    print(f"Wrote {OUT_META}")
    print(f"Wrote {OUT_OMEGA}")
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
