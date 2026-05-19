#!/usr/bin/env python3
"""Build a first public-covariance proxy for the likelihood-native source split.

This is a covariance propagation preflight, not a full likelihood product. It
uses public Pantheon+ and DESI covariance inputs, propagates them through the
current binned/anchored source-split transform, and assumes zero SN-BAO
cross-covariance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked
from fmc.public_data import load_flat_covariance_with_size, load_pantheon_table

PANTHEON_TABLE = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_ROWS = ROOT / "evidence" / "bao_residual_transform_preflight.csv"
BAO_COV = ROOT / "evidence" / "bao_residual_transform_covariance.csv"
DIAGNOSTIC = ROOT / "evidence" / "diagnostic_point_audit.csv"
SN_BINS = ROOT / "evidence" / "sn_residual_binned_preflight.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"

OUT_COV = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy.csv"
OUT_MARGINAL = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
OUT_SCORECARD = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_scorecard.csv"
OUT_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_summary.csv"


def grid_edges(grid: np.ndarray) -> np.ndarray:
    mids = (grid[:-1] + grid[1:]) / 2.0
    return np.concatenate([[max(0.0, grid[0] - (mids[0] - grid[0]))], mids, [grid[-1] + (grid[-1] - mids[-1])]])


def sn_bin_matrix(grid: np.ndarray, table: pd.DataFrame, covariance: np.ndarray) -> np.ndarray:
    """Return matrix mapping SN residuals to binned centered residual means."""
    z_col = "zHD" if "zHD" in table.columns else "zCMB"
    z = table[z_col].to_numpy(float)
    sigma_diag = np.sqrt(np.diag(covariance))
    weights_all = np.where(sigma_diag > 0.0, 1.0 / (sigma_diag * sigma_diag), 0.0)
    offset_weights = weights_all / float(np.sum(weights_all))
    centering = np.eye(len(table)) - np.ones((len(table), 1)) @ offset_weights.reshape(1, -1)

    edges = grid_edges(grid)
    bin_index = np.digitize(z, edges) - 1
    binner = np.zeros((len(grid), len(table)), dtype=float)
    for idx in range(len(grid)):
        members = np.where(bin_index == idx)[0]
        if len(members) == 0:
            continue
        weights = weights_all[members]
        denom = float(np.sum(weights))
        if denom <= 0.0:
            continue
        binner[idx, members] = weights / denom
    return binner @ centering


def load_bao_residual_covariance() -> tuple[pd.DataFrame, np.ndarray]:
    rows = pd.read_csv(BAO_ROWS)
    rows = rows[rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].reset_index(drop=True)
    cov_rows = pd.read_csv(BAO_COV)
    cov_rows = cov_rows[cov_rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].sort_values("CovRow")
    value_cols = [col for col in cov_rows.columns if col not in {"ProductID", "CovRow"}]
    cov = cov_rows[value_cols].to_numpy(float)
    return rows, cov


def weighted_anchor_matrix(grid: np.ndarray, bao_rows: pd.DataFrame, bao_cov: np.ndarray) -> np.ndarray:
    """Return matrix mapping BAO log residual rows to nearest-anchor means."""
    z_bao = bao_rows["z"].to_numpy(float)
    sigma = np.sqrt(np.diag(bao_cov))
    matrix = np.zeros((len(grid), len(bao_rows)), dtype=float)
    for i, z in enumerate(grid):
        distances = np.abs(z_bao - float(z))
        nearest_distance = float(np.min(distances))
        members = np.where(distances == nearest_distance)[0]
        weights = np.where(sigma[members] > 0.0, 1.0 / (sigma[members] * sigma[members]), 0.0)
        denom = float(np.sum(weights))
        if denom <= 0.0:
            continue
        matrix[i, members] = weights / denom
    return matrix


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> list[tuple[str, np.ndarray, int, str]]:
    rows: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_RHO4", w_k2_locked(x, rho=4.0) * k1, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    return rows


def main() -> None:
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

    # Standardized source split is SN/sigma_SN - BAO/sigma_BAO.
    sn_sigma = np.full(len(grid), np.nan)
    for _, row in sn_bins.iterrows():
        sn_sigma[int(row["GridIndex"])] = float(row["SigmaDiagProxy"])
    bao_sigma = np.sqrt(np.diag(bao_cov))
    d_sn = np.diag(np.where(np.isfinite(sn_sigma) & (sn_sigma > 0.0), 1.0 / sn_sigma, 0.0))
    d_bao = np.diag(np.where(bao_sigma > 0.0, 1.0 / bao_sigma, 0.0))
    standardized_cov_full = d_sn @ sn_cov @ d_sn + d_bao @ bao_cov @ d_bao

    usable_indices = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]["GridIndex"].astype(int).to_list()
    cov = standardized_cov_full[np.ix_(usable_indices, usable_indices)]
    # Tiny jitter for numerical safety only; does not change interpretation.
    cov = cov + np.eye(len(cov)) * 1e-12

    cov_df = pd.DataFrame(cov, columns=[str(idx) for idx in usable_indices])
    cov_df.insert(0, "GridIndex", usable_indices)
    cov_df.insert(0, "CovarianceID", "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1")
    cov_df["CovarianceStatus"] = "public_covariance_proxy_not_full_likelihood"
    cov_df["ClaimBoundary"] = "public_covariance_proxy_no_measurement_validation"
    cov_df.to_csv(OUT_COV, index=False)

    marginal = pd.DataFrame(
        {
            "CovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
            "GridIndex": usable_indices,
            "SigmaPublicProxy": np.sqrt(np.diag(cov)),
            "CovarianceStatus": "public_covariance_proxy_not_full_likelihood",
            "Assumption": "SN_BAO_cross_covariance_set_to_zero;standardized_linear_proxy",
            "ClaimBoundary": "public_covariance_proxy_no_measurement_validation",
        }
    )
    marginal.to_csv(OUT_MARGINAL, index=False)

    data = (
        external.merge(
            target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
            on="GridIndex",
            how="inner",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data = data[data["GridIndex"].isin(usable_indices)].copy()
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows = []
    for model_id, pred, k, model_class in model_rows(x, y, k1):
        c2 = chi2(y, pred, cov)
        rows.append(
            {
                "CovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "SignStableViolations": int(np.sum(np.sign(pred[stable]) != np.sign(y[stable]))),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "ClaimBoundary": "public_covariance_proxy_no_measurement_validation",
            }
        )
    scorecard = pd.DataFrame(rows)
    scorecard.to_csv(OUT_SCORECARD, index=False)

    best = scorecard.loc[scorecard["AIC"].idxmin()]
    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    k2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
    best_poly_aic = float(scorecard[scorecard["ModelID"].str.startswith("POLY")]["AIC"].min())
    summary = pd.DataFrame(
        [
            {
                "CovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
                "Rows": len(y),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly_aic,
                "RawPublicCovariancesUsed": True,
                "SNBAOCrossCovarianceIncluded": False,
                "CovarianceStatus": "public_covariance_proxy_not_full_likelihood",
                "Interpretation": (
                    "k2_competitive_under_public_covariance_proxy"
                    if k2_aic < best_poly_aic
                    else "public_covariance_proxy_mixed_or_weakening"
                ),
                "ClaimBoundary": "public_covariance_proxy_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_MARGINAL}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
