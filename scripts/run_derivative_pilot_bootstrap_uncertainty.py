#!/usr/bin/env python3
"""Bootstrap the public derivative-pilot backreaction curve.

This is an uncertainty stress test for the fixed polynomial pilot route. It is
not a source-native symbolic-regression bootstrap, does not fit K2/K1, and does
not authorize measurement validation.
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
PILOT_VECTOR = BR / "source_native_derivative_pilot_reconstruction_vector.csv"

OUT_BOOTSTRAP = BR / "source_native_derivative_pilot_bootstrap_omega_samples.csv"
OUT_COV = BR / "source_native_derivative_pilot_omega_covariance.csv"
OUT_BAND = BR / "source_native_derivative_pilot_omega_band.csv"
OUT_SUMMARY = EVIDENCE / "source_native_derivative_pilot_uncertainty_summary.csv"
OUT_DOC = DOCS / "source_native_derivative_pilot_uncertainty.md"

CLAIM_BOUNDARY = "source_native_derivative_pilot_uncertainty_no_measurement_validation"
FAMILY_ID = "PILOT_SN_BAO_POLY_D5_H3"


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


def build_omega_sample(
    sn_z: np.ndarray,
    sn_d: np.ndarray,
    sn_sigma: np.ndarray,
    bao_z: np.ndarray,
    bao_h: np.ndarray,
    bao_sigma: np.ndarray,
    grid: np.ndarray,
    rng: np.random.Generator,
) -> np.ndarray:
    d_draw = rng.normal(sn_d, sn_sigma)
    h_draw = rng.normal(bao_h, bao_sigma)
    d_poly = weighted_polyfit(sn_z, d_draw, sn_sigma, 5)
    h_poly = weighted_polyfit(bao_z, h_draw, bao_sigma, 3)
    return omega_r_plus_3omega_q(
        grid,
        d_poly(grid),
        np.polyder(d_poly, 1)(grid),
        np.polyder(d_poly, 2)(grid),
        h_poly(grid),
        np.polyder(h_poly, 1)(grid),
    )


def main() -> None:
    BR.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    sn = pd.read_csv(SN_INPUT)
    bao = weighted_mean_by_z(pd.read_csv(BAO_INPUT))
    vector = pd.read_csv(PILOT_VECTOR)
    grid = vector["z"].to_numpy(float)
    central = omega_r_plus_3omega_q(
        vector["z"],
        vector["D"],
        vector["D_prime"],
        vector["D_double_prime"],
        vector["H_D"],
        vector["H_D_prime"],
    )

    sn_z = sn["z"].to_numpy(float)
    sn_d = sn["D_proxy_Mpc"].to_numpy(float)
    sn_sigma = sn["D_proxy_sigma_diag_Mpc"].to_numpy(float)
    bao_z = bao["z"].to_numpy(float)
    bao_h = bao["Hrs_over_c_proxy"].to_numpy(float)
    bao_sigma = bao["Hrs_over_c_sigma_proxy"].to_numpy(float)

    rng = np.random.default_rng(20260518)
    samples = []
    sample_count = 128
    failed = 0
    for sample_id in range(sample_count):
        try:
            omega = build_omega_sample(sn_z, sn_d, sn_sigma, bao_z, bao_h, bao_sigma, grid, rng)
            if not np.isfinite(omega).all():
                failed += 1
                continue
            for z_value, omega_value in zip(grid, omega, strict=True):
                samples.append(
                    {
                        "FamilyID": FAMILY_ID,
                        "SampleID": sample_id,
                        "z": float(z_value),
                        "Omega_R_plus_3Omega_Q": float(omega_value),
                        "Source": "public_SN_BAO_training_input_bootstrap_pilot",
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
        except (np.linalg.LinAlgError, ValueError, FloatingPointError):
            failed += 1

    sample_df = pd.DataFrame(samples)
    sample_df.to_csv(OUT_BOOTSTRAP, index=False)

    pivot = sample_df.pivot_table(index="SampleID", columns="z", values="Omega_R_plus_3Omega_Q", aggfunc="first")
    sample_matrix = pivot.to_numpy(float)
    cov = np.cov(sample_matrix, rowvar=False)
    cov_rows = []
    cov_z = [float(v) for v in pivot.columns]
    for i, zi in enumerate(cov_z):
        for j, zj in enumerate(cov_z):
            cov_rows.append(
                {
                    "FamilyID": FAMILY_ID,
                    "z_i": zi,
                    "z_j": zj,
                    "Covariance": float(cov[i, j]),
                    "Source": "source_native_derivative_pilot_bootstrap_omega_samples",
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(cov_rows).to_csv(OUT_COV, index=False)

    band = pd.DataFrame(
        {
            "FamilyID": FAMILY_ID,
            "z": cov_z,
            "OmegaCentral": central,
            "OmegaMeanBootstrap": np.mean(sample_matrix, axis=0),
            "OmegaP16": np.percentile(sample_matrix, 16, axis=0),
            "OmegaP50": np.percentile(sample_matrix, 50, axis=0),
            "OmegaP84": np.percentile(sample_matrix, 84, axis=0),
            "OmegaSigmaBootstrap": np.std(sample_matrix, axis=0, ddof=1),
            "Source": "source_native_derivative_pilot_bootstrap_omega_samples",
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
    )
    band.to_csv(OUT_BAND, index=False)

    eig_min = float(np.linalg.eigvalsh(0.5 * (cov + cov.T)).min())
    rel_sigma = np.divide(
        band["OmegaSigmaBootstrap"].to_numpy(float),
        np.maximum(np.abs(band["OmegaCentral"].to_numpy(float)), 1e-12),
    )
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_DERIVATIVE_PILOT_UNCERTAINTY_V1",
                "RequestedSamples": sample_count,
                "SuccessfulSamples": int(pivot.shape[0]),
                "FailedSamples": failed,
                "GridRows": len(cov_z),
                "CovarianceEigenMin": eig_min,
                "CovariancePositiveSemidefinite": eig_min >= -1e-10,
                "MedianRelativeOmegaSigma": float(np.nanmedian(rel_sigma)),
                "MaxRelativeOmegaSigma": float(np.nanmax(rel_sigma)),
                "BootstrapUncertaintyReady": bool(pivot.shape[0] >= 16 and eig_min >= -1e-8),
                "SourceNativeUncertaintyReady": False,
                "K2FitPerformed": False,
                "K1RefitPerformed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "DERIVATIVE_PILOT_BOOTSTRAP_READY_SOURCE_NATIVE_UNCERTAINTY_MISSING",
                "StrongestAllowedClaim": (
                    "the public derivative pilot has a bootstrap uncertainty stress test for formula-path diagnostics"
                ),
                "PrimaryResidualRisk": (
                    "bootstrap uses diagonal public training-input errors and fixed polynomial degrees, not source-native symbolic-regression uncertainty"
                ),
                "NextAction": "propagate pilot bootstrap through K2 component split, then replace with source-native bootstrap/covariance when available",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Derivative Pilot Uncertainty",
                "",
                "Status: bootstrap uncertainty stress test ready; source-native uncertainty still missing.",
                "",
                "This bootstrap perturbs public SN distance-proxy and radial BAO H_D-proxy training inputs using diagonal errors, refits the fixed polynomial pilot, and propagates the fixed backreaction formula. It is not the published symbolic-regression bootstrap.",
                "",
                "## Outputs",
                "",
                f"- Bootstrap samples: `{OUT_BOOTSTRAP.relative_to(ROOT)}`",
                f"- Omega covariance: `{OUT_COV.relative_to(ROOT)}`",
                f"- Omega band: `{OUT_BAND.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_BOOTSTRAP}")
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_BAND}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
