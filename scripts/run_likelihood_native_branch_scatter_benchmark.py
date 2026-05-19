#!/usr/bin/env python3
"""Run a branch-scatter covariance preflight benchmark for likelihood-native K2."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.covariance import constant_offdiagonal, diagonal, nearest_neighbor
from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
FAMILY_EXPORT = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
SCATTER = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_covariance.csv"
SCORECARD = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_scorecard.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_summary.csv"


def load_data() -> pd.DataFrame:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]]
    families = pd.read_csv(FAMILY_EXPORT)
    grouped = (
        families.groupby("GridIndex")
        .agg(
            BranchCount=("ResponseValue", "count"),
            BranchMean=("ResponseValue", "mean"),
            BranchScatterSigma=("ResponseValue", "std"),
        )
        .reset_index()
    )
    data = (
        external.merge(target, on="GridIndex", how="inner")
        .merge(grouped, on="GridIndex", how="inner")
        .sort_values("GridIndex")
    )
    data["BranchScatterSigma"] = data["BranchScatterSigma"].fillna(0.0)
    data["ScatterFractionOfTarget"] = data["BranchScatterSigma"] / np.maximum(
        data["SourceSplitResponse"].abs(), 1e-12
    )
    data["SigmaNative"] = data["K1Sigma"].astype(float)
    data["SigmaBranchScatter"] = data["BranchScatterSigma"].astype(float)
    data["SigmaCombinedQuadrature"] = np.sqrt(data["SigmaNative"] ** 2 + data["SigmaBranchScatter"] ** 2)
    data["SigmaMaxNativeScatter"] = np.maximum(data["SigmaNative"], data["SigmaBranchScatter"])
    return data


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


def covariance_cases(data: pd.DataFrame) -> dict[str, np.ndarray]:
    native = data["SigmaNative"].to_numpy(float)
    scatter = data["SigmaBranchScatter"].to_numpy(float)
    combined = data["SigmaCombinedQuadrature"].to_numpy(float)
    max_sigma = data["SigmaMaxNativeScatter"].to_numpy(float)
    return {
        "branch_scatter_diagonal": diagonal(scatter),
        "native_plus_branch_scatter_quadrature": diagonal(combined),
        "max_native_or_branch_scatter": diagonal(max_sigma),
        "branch_scatter_nearest_neighbor_corr_0p25": nearest_neighbor(scatter, rho_corr=0.25),
        "branch_scatter_constant_offdiag_corr_0p25": constant_offdiagonal(scatter, rho_corr=0.25),
    }


def main() -> None:
    data = load_data()
    data[
        [
            "GridIndex",
            "z_grid",
            "x_coordinate",
            "SourceSplitResponse",
            "BranchCount",
            "BranchMean",
            "BranchScatterSigma",
            "ScatterFractionOfTarget",
            "SigmaNative",
            "SigmaCombinedQuadrature",
            "SigmaMaxNativeScatter",
        ]
    ].assign(
        CovarianceStatus="branch_scatter_preflight_not_public_full_covariance",
        ClaimBoundary="branch_scatter_benchmark_no_measurement_validation",
    ).to_csv(SCATTER, index=False)

    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    rows = []
    for cov_id, cov in covariance_cases(data).items():
        for model_id, pred, k, model_class in model_rows(x, y, k1):
            c2 = chi2(y, pred, cov)
            rows.append(
                {
                    "CovarianceCase": cov_id,
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(y),
                    "ParameterCount": k,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "SignStableViolations": int(np.sum(np.sign(pred[stable]) != np.sign(y[stable]))),
                    "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                    "MinSigmaEffective": float(np.sqrt(np.min(np.diag(cov)))),
                    "MaxSigmaEffective": float(np.sqrt(np.max(np.diag(cov)))),
                    "ClaimBoundary": "branch_scatter_benchmark_no_measurement_validation",
                }
            )
    scorecard = pd.DataFrame(rows)
    scorecard.to_csv(SCORECARD, index=False)

    summary_rows = []
    for cov_id, group in scorecard.groupby("CovarianceCase", sort=False):
        best = group.loc[group["AIC"].idxmin()]
        k1_aic = float(group.loc[group["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
        k2_aic = float(group.loc[group["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
        best_poly_aic = float(group[group["ModelID"].str.startswith("POLY")]["AIC"].min())
        summary_rows.append(
            {
                "CovarianceCase": cov_id,
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly_aic,
                "Interpretation": (
                    "k2_competitive_under_branch_scatter_preflight"
                    if k2_aic < best_poly_aic
                    else "poly_control_dominates_under_branch_scatter_preflight"
                ),
                "ClaimBoundary": "branch_scatter_benchmark_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {SCATTER}")
    print(f"Wrote {SCORECARD}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
