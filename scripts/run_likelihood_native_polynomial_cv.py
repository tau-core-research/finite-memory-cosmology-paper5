#!/usr/bin/env python3
"""Cross-validate polynomial controls on the likelihood-native source split.

This checks whether the polynomial controls that dominate the public covariance
proxy are stable out of sample. It does not refit K1, change K2, or promote a
measurement-validation claim.
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
OUT = ROOT / "evidence" / "source_split_likelihood_native_polynomial_cv.csv"
OUT_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_polynomial_cv_summary.csv"


def weighted_poly_predict(
    x_train: np.ndarray,
    y_train: np.ndarray,
    sigma_train: np.ndarray,
    x_test: np.ndarray,
    degree: int,
) -> np.ndarray:
    weights = np.where(sigma_train > 0.0, 1.0 / sigma_train, 0.0)
    coeff = np.polyfit(x_train, y_train, degree, w=weights)
    return np.polyval(coeff, x_test)


def fold_masks(x: np.ndarray, stable: np.ndarray) -> dict[str, np.ndarray]:
    masks: dict[str, np.ndarray] = {}
    for idx in range(len(x)):
        test = np.zeros(len(x), dtype=bool)
        test[idx] = True
        masks[f"loo_row_{idx}"] = test
    masks["low_depth_block"] = x <= 1 / 3
    masks["mid_depth_block"] = (x > 1 / 3) & (x <= 2 / 3)
    masks["high_depth_block"] = x > 2 / 3
    masks["sign_stable_block"] = stable
    masks["sign_unstable_block"] = ~stable
    return masks


def load_data() -> pd.DataFrame:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    public = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    branch = pd.read_csv(BRANCH_SCATTER)[["GridIndex", "BranchScatterSigma", "SigmaCombinedQuadrature"]]
    return (
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


def main() -> None:
    data = load_data()
    x = data["x_coordinate_k1"].to_numpy(float)
    z = data["z_grid_k1"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2 = w_k2_locked(x, rho=4.0) * k1
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    sigma_routes = {
        "public_proxy_diag": data["SigmaPublicProxy"].to_numpy(float),
        "branch_scatter_diag": data["BranchScatterSigma"].to_numpy(float),
        "native_plus_branch_scatter_quadrature": data["SigmaCombinedQuadrature"].to_numpy(float),
    }

    rows = []
    for sigma_route, sigma in sigma_routes.items():
        for fold_id, test in fold_masks(x, stable).items():
            train = ~test
            if int(test.sum()) < 1:
                continue
            if int(train.sum()) < 5:
                # Need enough points to fit degree-3 without turning this into
                # a nearly saturated interpolation artifact.
                continue
            models: list[tuple[str, np.ndarray, int, str]] = [
                ("K1_NO_MEMORY", k1[test], 0, "fair_null"),
                ("K2_LOCKED_RHO4", k2[test], 0, "locked_prediction"),
            ]
            for degree in [2, 3]:
                pred = weighted_poly_predict(x[train], y[train], sigma[train], x[test], degree)
                models.append((f"POLY_DEG{degree}", pred, degree + 1, "overfit_risk_control"))
            for model_id, pred, parameter_count, model_class in models:
                residual = y[test] - pred
                chi2_values = (residual / sigma[test]) ** 2
                rows.append(
                    {
                        "Dataset": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_PREFLIGHT",
                        "SigmaRoute": sigma_route,
                        "ValidationMode": "leave_one_out" if fold_id.startswith("loo") else "blocked_split",
                        "FoldID": fold_id,
                        "ModelID": model_id,
                        "ModelClass": model_class,
                        "ParameterCount": parameter_count,
                        "TrainN": int(train.sum()),
                        "TestN": int(test.sum()),
                        "TestGridIndices": ";".join(str(int(v)) for v in data.loc[test, "GridIndex"]),
                        "TestZMin": float(np.min(z[test])),
                        "TestZMax": float(np.max(z[test])),
                        "TestChi2": float(np.sum(chi2_values)),
                        "TestMeanChi2": float(np.mean(chi2_values)),
                        "TestMeanAbsResidual": float(np.mean(np.abs(residual))),
                        "ClaimBoundary": "polynomial_cv_no_measurement_validation",
                    }
                )

    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (sigma_route, validation_mode, model_id), group in detail.groupby(
        ["SigmaRoute", "ValidationMode", "ModelID"], sort=False
    ):
        summary_rows.append(
            {
                "SigmaRoute": sigma_route,
                "ValidationMode": validation_mode,
                "ModelID": model_id,
                "Folds": int(len(group)),
                "TotalTestN": int(group["TestN"].sum()),
                "TotalTestChi2": float(group["TestChi2"].sum()),
                "MeanFoldChi2": float(group["TestChi2"].mean()),
                "MeanTestMeanChi2": float(group["TestMeanChi2"].mean()),
                "MeanAbsResidual": float(group["TestMeanAbsResidual"].mean()),
                "ClaimBoundary": "polynomial_cv_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)

    comparison_rows = []
    for (sigma_route, validation_mode), group in summary.groupby(["SigmaRoute", "ValidationMode"], sort=False):
        k2_row = group[group["ModelID"].eq("K2_LOCKED_RHO4")].iloc[0]
        best_poly = group[group["ModelID"].str.startswith("POLY")].sort_values("TotalTestChi2").iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        comparison_rows.append(
            {
                "SigmaRoute": sigma_route,
                "ValidationMode": validation_mode,
                "ModelID": "CV_COMPARISON",
                "Folds": int(k2_row["Folds"]),
                "TotalTestN": int(k2_row["TotalTestN"]),
                "TotalTestChi2": float(k2_row["TotalTestChi2"]),
                "MeanFoldChi2": float(k2_row["MeanFoldChi2"]),
                "MeanTestMeanChi2": float(k2_row["MeanTestMeanChi2"]),
                "MeanAbsResidual": float(k2_row["MeanAbsResidual"]),
                "K1TotalTestChi2": float(k1_row["TotalTestChi2"]),
                "BestPolyModel": best_poly["ModelID"],
                "BestPolyTotalTestChi2": float(best_poly["TotalTestChi2"]),
                "DeltaChi2_K2_minus_K1": float(k2_row["TotalTestChi2"] - k1_row["TotalTestChi2"]),
                "DeltaChi2_K2_minus_BestPoly": float(k2_row["TotalTestChi2"] - best_poly["TotalTestChi2"]),
                "K2ImprovesOverK1": bool(k2_row["TotalTestChi2"] < k1_row["TotalTestChi2"]),
                "K2BeatsBestPoly": bool(k2_row["TotalTestChi2"] < best_poly["TotalTestChi2"]),
                "ClaimBoundary": "polynomial_cv_no_measurement_validation",
            }
        )
    summary = pd.concat([summary, pd.DataFrame(comparison_rows)], ignore_index=True, sort=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
