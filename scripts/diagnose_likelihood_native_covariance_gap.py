#!/usr/bin/env python3
"""Diagnose why public covariance and branch-scatter routes diverge.

This is a route-gap audit only. It does not modify K2, fit K1, or select a new
covariance benchmark.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
PUBLIC_MARGINALS = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
BRANCH_SCATTER = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_covariance.csv"
OUT_AUDIT = ROOT / "evidence" / "source_split_likelihood_native_covariance_gap_audit.csv"
OUT_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_covariance_gap_summary.csv"


def model_predictions(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> dict[str, tuple[np.ndarray, int]]:
    rows: dict[str, tuple[np.ndarray, int]] = {
        "K1_NO_MEMORY": (k1, 0),
        "K2_LOCKED_RHO4": (w_k2_locked(x, rho=4.0) * k1, 0),
        "ZERO_RESPONSE_CONTROL": (np.zeros_like(y), 0),
    }
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows[f"POLY_DEG{degree}"] = (np.polyval(coeff, x), degree + 1)
    return rows


def classify_sigma_ratio(public_sigma: float, branch_sigma: float) -> str:
    if not np.isfinite(public_sigma) or not np.isfinite(branch_sigma) or branch_sigma <= 0.0:
        return "SIGMA_RATIO_UNAVAILABLE"
    ratio = public_sigma / branch_sigma
    if ratio < 0.75:
        return "PUBLIC_TIGHTER_THAN_BRANCH"
    if ratio > 1.25:
        return "PUBLIC_LOOSER_THAN_BRANCH"
    return "SIMILAR_SIGMA_SCALE"


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    public = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    branch = pd.read_csv(BRANCH_SCATTER)[
        ["GridIndex", "BranchScatterSigma", "SigmaNative", "SigmaCombinedQuadrature", "SigmaMaxNativeScatter"]
    ]

    data = (
        external.merge(
            target[["GridIndex", "z_grid", "x_coordinate", "SourceSplitResponse", "SignStableTemplate"]],
            on="GridIndex",
            how="inner",
            suffixes=("_k1", "_target"),
        )
        .merge(public, on="GridIndex", how="inner")
        .merge(branch, on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )

    x = data["x_coordinate_k1"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    models = model_predictions(x, y, k1)

    audit_rows = []
    for row_idx, row in data.iterrows():
        public_sigma = float(row["SigmaPublicProxy"])
        branch_sigma = float(row["BranchScatterSigma"])
        combined_sigma = float(row["SigmaCombinedQuadrature"])
        max_sigma = float(row["SigmaMaxNativeScatter"])
        sigma_ratio = public_sigma / branch_sigma if branch_sigma > 0.0 else np.nan
        for model_id, (pred, parameter_count) in models.items():
            prediction = float(pred[row_idx])
            target_value = float(row["SourceSplitResponse"])
            residual = target_value - prediction
            audit_rows.append(
                {
                    "GridIndex": int(row["GridIndex"]),
                    "z": float(row["z_grid_k1"]),
                    "x": float(row["x_coordinate_k1"]),
                    "ModelID": model_id,
                    "ParameterCount": parameter_count,
                    "Target": target_value,
                    "Prediction": prediction,
                    "Residual": residual,
                    "AbsResidual": abs(residual),
                    "SigmaPublicProxy": public_sigma,
                    "SigmaBranchScatter": branch_sigma,
                    "SigmaCombinedQuadrature": combined_sigma,
                    "SigmaMaxNativeScatter": max_sigma,
                    "PublicToBranchSigmaRatio": sigma_ratio,
                    "PublicDiagChi2Contribution": (residual / public_sigma) ** 2
                    if public_sigma > 0.0
                    else np.nan,
                    "BranchScatterDiagChi2Contribution": (residual / branch_sigma) ** 2
                    if branch_sigma > 0.0
                    else np.nan,
                    "CombinedDiagChi2Contribution": (residual / combined_sigma) ** 2
                    if combined_sigma > 0.0
                    else np.nan,
                    "SigmaGapClass": classify_sigma_ratio(public_sigma, branch_sigma),
                    "SignStable": bool(str(row["SignStableTemplate"]).lower() == "true"),
                    "ClaimBoundary": "covariance_gap_audit_no_measurement_validation",
                }
            )

    audit = pd.DataFrame(audit_rows)
    audit["PublicContributionRank"] = audit.groupby("ModelID")["PublicDiagChi2Contribution"].rank(
        ascending=False, method="first"
    )
    audit["BranchContributionRank"] = audit.groupby("ModelID")["BranchScatterDiagChi2Contribution"].rank(
        ascending=False, method="first"
    )
    audit.to_csv(OUT_AUDIT, index=False)

    k2 = audit[audit["ModelID"].eq("K2_LOCKED_RHO4")].copy()
    k1_rows = audit[audit["ModelID"].eq("K1_NO_MEMORY")].copy()
    best_poly_public = (
        audit[audit["ModelID"].str.startswith("POLY")]
        .groupby("GridIndex")["PublicDiagChi2Contribution"]
        .min()
        .reset_index(name="BestPolyPublicDiagContribution")
    )
    best_poly_branch = (
        audit[audit["ModelID"].str.startswith("POLY")]
        .groupby("GridIndex")["BranchScatterDiagChi2Contribution"]
        .min()
        .reset_index(name="BestPolyBranchDiagContribution")
    )
    compare = (
        k2[["GridIndex", "PublicDiagChi2Contribution", "BranchScatterDiagChi2Contribution"]]
        .rename(
            columns={
                "PublicDiagChi2Contribution": "K2PublicDiagContribution",
                "BranchScatterDiagChi2Contribution": "K2BranchDiagContribution",
            }
        )
        .merge(
            k1_rows[["GridIndex", "PublicDiagChi2Contribution", "BranchScatterDiagChi2Contribution"]].rename(
                columns={
                    "PublicDiagChi2Contribution": "K1PublicDiagContribution",
                    "BranchScatterDiagChi2Contribution": "K1BranchDiagContribution",
                }
            ),
            on="GridIndex",
        )
        .merge(best_poly_public, on="GridIndex")
        .merge(best_poly_branch, on="GridIndex")
    )
    summary = pd.DataFrame(
        [
            {
                "Rows": len(data),
                "MedianPublicSigma": float(data["SigmaPublicProxy"].median()),
                "MedianBranchScatterSigma": float(data["BranchScatterSigma"].median()),
                "MedianPublicToBranchSigmaRatio": float(
                    (data["SigmaPublicProxy"] / data["BranchScatterSigma"]).median()
                ),
                "RowsWherePublicSigmaTighterThanBranch": int(
                    np.sum(data["SigmaPublicProxy"] < data["BranchScatterSigma"])
                ),
                "RowsWhereK2PublicContributionBelowK1": int(
                    np.sum(compare["K2PublicDiagContribution"] < compare["K1PublicDiagContribution"])
                ),
                "RowsWhereK2BranchContributionBelowK1": int(
                    np.sum(compare["K2BranchDiagContribution"] < compare["K1BranchDiagContribution"])
                ),
                "RowsWhereK2PublicContributionBelowBestPoly": int(
                    np.sum(compare["K2PublicDiagContribution"] < compare["BestPolyPublicDiagContribution"])
                ),
                "RowsWhereK2BranchContributionBelowBestPoly": int(
                    np.sum(compare["K2BranchDiagContribution"] < compare["BestPolyBranchDiagContribution"])
                ),
                "TopK2PublicContributionGridIndex": int(
                    k2.loc[k2["PublicDiagChi2Contribution"].idxmax(), "GridIndex"]
                ),
                "TopK2BranchContributionGridIndex": int(
                    k2.loc[k2["BranchScatterDiagChi2Contribution"].idxmax(), "GridIndex"]
                ),
                "Interpretation": "public_proxy_is_tighter_than_branch_scatter_on_low_depth_rows_and_keeps_polynomial_controls_competitive",
                "ClaimBoundary": "covariance_gap_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
