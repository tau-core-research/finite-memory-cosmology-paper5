#!/usr/bin/env python3
"""Build an independent derivative pilot from public SN/BAO training inputs.

This script is a preflight diagnostic only. It does not reproduce the
source-native symbolic-regression families from the backreaction papers, does
not fit K2, and does not authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fmc.backreaction import omega_r_plus_3omega_q

ROOT = Path(__file__).resolve().parents[1]
BR = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SN_INPUT = BR / "source_native_training_sn_distance_proxy.csv"
BAO_INPUT = BR / "source_native_training_bao_hd_proxy.csv"

OUT_VECTOR = BR / "source_native_derivative_pilot_reconstruction_vector.csv"
OUT_OMEGA = BR / "source_native_derivative_pilot_omega_curve.csv"
OUT_SUMMARY = EVIDENCE / "source_native_derivative_pilot_summary.csv"
OUT_DOC = DOCS / "source_native_derivative_pilot.md"

CLAIM_BOUNDARY = "source_native_derivative_pilot_no_measurement_validation"
FAMILY_ID = "PILOT_SN_BAO_POLY_D5_H3"


def weighted_polyfit(x: np.ndarray, y: np.ndarray, sigma: np.ndarray, degree: int) -> np.poly1d:
    """Return a weighted polynomial fit using finite, positive uncertainties."""
    mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
    if int(mask.sum()) <= degree:
        raise ValueError(f"not enough finite points for degree {degree}: {int(mask.sum())}")
    weights = 1.0 / sigma[mask]
    coeff = np.polyfit(x[mask], y[mask], degree, w=weights)
    return np.poly1d(coeff)


def weighted_mean_by_z(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse duplicate BAO redshift rows with inverse-variance weights."""
    rows = []
    for z_value, group in df.groupby("z", sort=True):
        y = group["Hrs_over_c_proxy"].to_numpy(float)
        sigma = group["Hrs_over_c_sigma_proxy"].to_numpy(float)
        mask = np.isfinite(y) & np.isfinite(sigma) & (sigma > 0)
        if not mask.any():
            continue
        w = 1.0 / (sigma[mask] ** 2)
        mean = float(np.sum(w * y[mask]) / np.sum(w))
        err = float(np.sqrt(1.0 / np.sum(w)))
        rows.append(
            {
                "z": float(z_value),
                "Hrs_over_c_proxy": mean,
                "Hrs_over_c_sigma_proxy": err,
                "CollapsedRows": int(mask.sum()),
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

    d_degree = 5
    h_degree = 3
    d_poly = weighted_polyfit(sn_z, sn_d, sn_sigma, d_degree)
    h_poly = weighted_polyfit(bao_z, bao_h, bao_sigma, h_degree)

    d_prime = np.polyder(d_poly, 1)
    d_double_prime = np.polyder(d_poly, 2)
    h_prime = np.polyder(h_poly, 1)

    z_min = max(float(np.nanmin(bao_z)), float(np.nanmin(sn_z)))
    z_max = min(float(np.nanmax(bao_z)), float(np.nanmax(sn_z)))
    grid = np.linspace(z_min, z_max, 24)

    d_val = d_poly(grid)
    dp_val = d_prime(grid)
    dpp_val = d_double_prime(grid)
    h_val = h_poly(grid)
    hp_val = h_prime(grid)

    vector = pd.DataFrame(
        {
            "FamilyID": FAMILY_ID,
            "SampleID": 0,
            "z": grid,
            "D": d_val,
            "D_prime": dp_val,
            "D_double_prime": dpp_val,
            "H_D": h_val,
            "H_D_prime": hp_val,
            "Source": "public_SN_BAO_training_inputs_weighted_polynomial_pilot",
            "SelectionRule": "fixed_degree_D5_H3_no_K2_fit_no_source_native_claim",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    vector.to_csv(OUT_VECTOR, index=False)

    omega = omega_r_plus_3omega_q(
        vector["z"],
        vector["D"],
        vector["D_prime"],
        vector["D_double_prime"],
        vector["H_D"],
        vector["H_D_prime"],
    )
    omega_df = pd.DataFrame(
        {
            "FamilyID": FAMILY_ID,
            "SampleID": 0,
            "z": grid,
            "Omega_R_plus_3Omega_Q": omega,
            "Source": "source_native_derivative_pilot_reconstruction_vector",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    omega_df.to_csv(OUT_OMEGA, index=False)

    finite_vector = bool(np.isfinite(vector[["D", "D_prime", "D_double_prime", "H_D", "H_D_prime"]].to_numpy()).all())
    nonzero_denominators = bool((np.abs(vector["D"].to_numpy(float)) > 0).all() and (np.abs(vector["H_D"].to_numpy(float)) > 0).all())
    finite_omega = bool(np.isfinite(omega).all())

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_DERIVATIVE_PILOT_V1",
                "FamilyID": FAMILY_ID,
                "SNInputRows": len(sn),
                "BAOUniqueRedshiftRows": len(bao),
                "GridRows": len(grid),
                "DPolynomialDegree": d_degree,
                "HDPolynomialDegree": h_degree,
                "ZMin": float(grid.min()),
                "ZMax": float(grid.max()),
                "FiniteDerivativeVector": finite_vector,
                "NonZeroFormulaDenominators": nonzero_denominators,
                "FiniteOmegaCurve": finite_omega,
                "OmegaMin": float(np.nanmin(omega)),
                "OmegaMax": float(np.nanmax(omega)),
                "OmegaMedian": float(np.nanmedian(omega)),
                "DerivativePilotReady": finite_vector and nonzero_denominators and finite_omega,
                "SourceNativeExportReady": False,
                "CovarianceReady": False,
                "K2FitPerformed": False,
                "K1RefitPerformed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "DERIVATIVE_PILOT_READY_SOURCE_NATIVE_EXPORTS_STILL_MISSING",
                "StrongestAllowedClaim": (
                    "public SN/BAO training inputs can drive a fixed polynomial derivative pilot for formula-path stress testing"
                ),
                "PrimaryResidualRisk": (
                    "weighted polynomial pilot is not the published symbolic-regression family and has no source-native covariance"
                ),
                "NextAction": "compare pilot omega shape to the provisional bridge, then replace with author/source-native family exports when available",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Derivative Pilot",
                "",
                "Status: derivative pilot ready; source-native exports still missing.",
                "",
                "This pilot fits fixed weighted polynomials to the public SN distance-proxy and radial BAO H_D-proxy training inputs, then evaluates the fixed backreaction formula. It is an engineering stress test for the formula path, not a reproduction of the published symbolic-regression families.",
                "",
                "## Outputs",
                "",
                f"- Reconstruction vector: `{OUT_VECTOR.relative_to(ROOT)}`",
                f"- Omega curve: `{OUT_OMEGA.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Claim Boundary",
                "",
                "No K2 fit, no K1 refit, no source-native covariance, and no measurement validation are authorized by this pilot.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_VECTOR}")
    print(f"Wrote {OUT_OMEGA}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
