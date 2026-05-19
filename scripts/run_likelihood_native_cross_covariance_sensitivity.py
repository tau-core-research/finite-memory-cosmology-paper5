#!/usr/bin/env python3
"""Cross-covariance sensitivity for the likelihood-native public covariance proxy."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_likelihood_native_public_covariance_proxy import (  # type: ignore
    BAO_COV,
    BAO_ROWS,
    DIAGNOSTIC,
    EXTERNAL_K1,
    PANTHEON_COV,
    PANTHEON_TABLE,
    SN_BINS,
    TARGET,
    load_bao_residual_covariance,
    model_rows,
    sn_bin_matrix,
    weighted_anchor_matrix,
)
from fmc.likelihood import aic, bic, chi2
from fmc.public_data import load_flat_covariance_with_size, load_pantheon_table

OUT = ROOT / "evidence" / "source_split_likelihood_native_cross_covariance_sensitivity.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_cross_covariance_summary.csv"


def standardized_components() -> tuple[list[int], np.ndarray, np.ndarray, pd.DataFrame]:
    diagnostic = pd.read_csv(DIAGNOSTIC)
    grid = diagnostic["z"].to_numpy(float)
    sn_bins = pd.read_csv(SN_BINS)
    target = pd.read_csv(TARGET)
    external = pd.read_csv(EXTERNAL_K1)

    pantheon_table = load_pantheon_table(PANTHEON_TABLE)
    pantheon_cov = load_flat_covariance_with_size(PANTHEON_COV)
    sn_matrix = sn_bin_matrix(grid, pantheon_table, pantheon_cov)
    sn_cov = sn_matrix @ pantheon_cov @ sn_matrix.T

    bao_rows, bao_cov_raw = load_bao_residual_covariance()
    bao_matrix = weighted_anchor_matrix(grid, bao_rows, bao_cov_raw)
    bao_cov = bao_matrix @ bao_cov_raw @ bao_matrix.T

    sn_sigma = np.full(len(grid), np.nan)
    for _, row in sn_bins.iterrows():
        sn_sigma[int(row["GridIndex"])] = float(row["SigmaDiagProxy"])
    bao_sigma = np.sqrt(np.diag(bao_cov))
    d_sn = np.diag(np.where(np.isfinite(sn_sigma) & (sn_sigma > 0.0), 1.0 / sn_sigma, 0.0))
    d_bao = np.diag(np.where(bao_sigma > 0.0, 1.0 / bao_sigma, 0.0))
    sn_std = d_sn @ sn_cov @ d_sn
    bao_std = d_bao @ bao_cov @ d_bao

    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]["GridIndex"].astype(int).to_list()
    data = (
        external.merge(
            target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
            on="GridIndex",
            how="inner",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data = data[data["GridIndex"].isin(usable)].copy()
    return usable, sn_std[np.ix_(usable, usable)], bao_std[np.ix_(usable, usable)], data


def cross_covariance(sn_cov: np.ndarray, bao_cov: np.ndarray, rho_cross: float) -> np.ndarray:
    sn_sigma = np.sqrt(np.maximum(np.diag(sn_cov), 0.0))
    bao_sigma = np.sqrt(np.maximum(np.diag(bao_cov), 0.0))
    # Row-aligned cross-covariance proxy only. Full SN-BAO cross-covariance is unknown.
    cross = np.diag(float(rho_cross) * sn_sigma * bao_sigma)
    return sn_cov + bao_cov - cross - cross.T


def positive_definite(cov: np.ndarray) -> bool:
    try:
        np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        return False
    return True


def main() -> None:
    usable, sn_cov, bao_cov, data = standardized_components()
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows = []
    rho_values = np.round(np.linspace(-0.9, 0.9, 37), 3)
    for rho_cross in rho_values:
        cov = cross_covariance(sn_cov, bao_cov, float(rho_cross))
        cov = cov + np.eye(len(cov)) * 1e-12
        is_pd = positive_definite(cov)
        if not is_pd:
            rows.append(
                {
                    "RhoCross": float(rho_cross),
                    "ModelID": "",
                    "ModelClass": "",
                    "Rows": len(usable),
                    "PositiveDefinite": False,
                    "ParameterCount": "",
                    "Chi2": "",
                    "AIC": "",
                    "BIC": "",
                    "SignStableViolations": "",
                    "ClaimBoundary": "cross_covariance_sensitivity_no_measurement_validation",
                }
            )
            continue
        for model_id, pred, k, model_class in model_rows(x, y, k1):
            c2 = chi2(y, pred, cov)
            rows.append(
                {
                    "RhoCross": float(rho_cross),
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(usable),
                    "PositiveDefinite": True,
                    "ParameterCount": k,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "SignStableViolations": int(np.sum(np.sign(pred[stable]) != np.sign(y[stable]))),
                    "ClaimBoundary": "cross_covariance_sensitivity_no_measurement_validation",
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    valid = output[output["PositiveDefinite"].astype(str).str.lower().eq("true")].copy()
    valid["AIC"] = pd.to_numeric(valid["AIC"])
    summary_rows = []
    for rho_cross, group in valid.groupby("RhoCross", sort=True):
        best = group.loc[group["AIC"].idxmin()]
        k2_aic = float(group.loc[group["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
        k1_aic = float(group.loc[group["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
        best_poly = float(group[group["ModelID"].str.startswith("POLY")]["AIC"].min())
        summary_rows.append(
            {
                "RhoCross": float(rho_cross),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly,
                "Interpretation": (
                    "k2_competitive_under_cross_covariance_proxy"
                    if k2_aic < best_poly
                    else "poly_control_dominates_under_cross_covariance_proxy"
                ),
                "ClaimBoundary": "cross_covariance_sensitivity_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
