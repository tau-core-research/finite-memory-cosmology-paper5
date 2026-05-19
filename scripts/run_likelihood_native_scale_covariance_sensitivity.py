#!/usr/bin/env python3
"""Scale/covariance sensitivity for likelihood-native source-split scorecard."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.covariance import constant_offdiagonal, diagonal, exponential_in_x, exponential_in_z, nearest_neighbor
from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
OUT = ROOT / "evidence" / "source_split_likelihood_native_scale_covariance_sensitivity.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_scale_covariance_summary.csv"


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> list[tuple[str, np.ndarray, int]]:
    rows: list[tuple[str, np.ndarray, int]] = [
        ("K1_NO_MEMORY", k1, 0),
        ("K2_LOCKED_RHO4", w_k2_locked(x, rho=4.0) * k1, 0),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1))
    return rows


def covariance_cases(sigma: np.ndarray, z: np.ndarray, x: np.ndarray, y: np.ndarray) -> dict[str, np.ndarray]:
    abs_y = np.abs(y)
    return {
        "diag_native_sigma": diagonal(sigma),
        "diag_sigma_floor_0p10": diagonal(np.maximum(sigma, 0.10)),
        "diag_sigma_floor_0p25": diagonal(np.maximum(sigma, 0.25)),
        "diag_target_fraction_floor_10pct": diagonal(np.maximum(sigma, 0.10 * abs_y)),
        "diag_target_fraction_floor_25pct": diagonal(np.maximum(sigma, 0.25 * abs_y)),
        "nearest_neighbor_corr_0p25": nearest_neighbor(sigma, rho_corr=0.25),
        "constant_offdiag_corr_0p25": constant_offdiagonal(sigma, rho_corr=0.25),
        "exp_corr_z": exponential_in_z(sigma, z),
        "exp_corr_x": exponential_in_x(sigma, x),
    }


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    z = data["z_grid"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    sigma = data["K1Sigma"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows = []
    for cov_id, cov in covariance_cases(sigma, z, x, y).items():
        for model_id, pred, k in model_rows(x, y, k1):
            c2 = chi2(y, pred, cov)
            rows.append(
                {
                    "CovarianceCase": cov_id,
                    "ModelID": model_id,
                    "ParameterCount": k,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "SignStableViolations": int(np.sum(np.sign(pred[stable]) != np.sign(y[stable]))),
                    "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                    "MinSigmaEffective": float(np.sqrt(np.min(np.diag(cov)))),
                    "MaxSigmaEffective": float(np.sqrt(np.max(np.diag(cov)))),
                    "ClaimBoundary": "scale_covariance_sensitivity_only_no_measurement_validation",
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary_rows = []
    for cov_id, group in output.groupby("CovarianceCase", sort=False):
        best = group.loc[group["AIC"].idxmin()]
        k1_aic = float(group.loc[group["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
        k2_aic = float(group.loc[group["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
        poly_aic = float(group[group["ModelID"].str.startswith("POLY")]["AIC"].min())
        summary_rows.append(
            {
                "CovarianceCase": cov_id,
                "BestModel": best["ModelID"],
                "BestAIC": float(best["AIC"]),
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < poly_aic,
                "Interpretation": (
                    "k2_competitive"
                    if k2_aic < poly_aic
                    else "poly_control_dominates"
                ),
                "ClaimBoundary": "scale_covariance_sensitivity_only_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
