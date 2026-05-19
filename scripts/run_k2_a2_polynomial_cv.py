#!/usr/bin/env python3
"""Cross-validate A2 against polynomial controls.

This extends the existing polynomial CV idea with the locked
K2_SOURCE_SPLIT_A2_PRIOR_V1 prediction. The A2 prediction is fixed and is not
refit on training folds.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PUBLIC_MARGINALS = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
BRANCH_SCATTER = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_polynomial_cv.csv"
SUMMARY = EVIDENCE / "k2_a2_polynomial_cv_summary.csv"


def weighted_poly_predict(x_train, y_train, sigma_train, x_test, degree: int) -> np.ndarray:
    weights = np.where(sigma_train > 0.0, 1.0 / sigma_train, 0.0)
    coeff = np.polyfit(x_train, y_train, degree, w=weights)
    return np.polyval(coeff, x_test)


def fold_masks(x: np.ndarray, stable: np.ndarray) -> dict[str, np.ndarray]:
    masks: dict[str, np.ndarray] = {}
    for idx in range(len(x)):
        test = np.zeros(len(x), dtype=bool)
        test[idx] = True
        masks[f"loo_row_{idx}"] = test
    masks["low_depth_block"] = x <= 0.5
    masks["mid_depth_block"] = (x > 0.5) & (x <= 0.8)
    masks["high_depth_block"] = x > 0.8
    masks["sign_stable_block"] = stable
    masks["sign_unstable_block"] = ~stable
    return masks


def main() -> None:
    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    public = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    branch = pd.read_csv(BRANCH_SCATTER)[["GridIndex", "BranchScatterSigma", "SigmaCombinedQuadrature"]]

    data = (
        target[target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])]
        [["GridIndex", "z_grid", "SourceSplitResponse", "SignStableTemplate"]]
        .merge(
            pred[
                [
                    "GridIndex",
                    "x_coordinate",
                    "K1Response",
                    "K2UnitLockedRho4",
                    "K2SourceSplitA2Prediction",
                ]
            ],
            on="GridIndex",
            how="inner",
        )
        .merge(public, on="GridIndex", how="inner")
        .merge(branch, on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )

    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2 = data["K2UnitLockedRho4"].to_numpy(float)
    a2 = data["K2SourceSplitA2Prediction"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy()

    sigma_routes = {
        "public_proxy_diag": data["SigmaPublicProxy"].to_numpy(float),
        "branch_scatter_diag": data["BranchScatterSigma"].to_numpy(float),
        "native_plus_branch_scatter_quadrature": data["SigmaCombinedQuadrature"].to_numpy(float),
    }

    rows = []
    for sigma_route, sigma in sigma_routes.items():
        for fold_id, test in fold_masks(x, stable).items():
            train = ~test
            if int(test.sum()) < 1 or int(train.sum()) < 5:
                continue
            models: list[tuple[str, np.ndarray, int, str]] = [
                ("K1_NO_MEMORY", k1[test], 0, "fair_null"),
                ("K2_UNIT_LOCKED_RHO4", k2[test], 0, "locked_memory_backbone"),
                ("K2_SOURCE_SPLIT_A2_PRIOR_V1", a2[test], 0, "locked_projection_prior"),
            ]
            for degree in [2, 3]:
                models.append(
                    (
                        f"POLY_DEG{degree}",
                        weighted_poly_predict(x[train], y[train], sigma[train], x[test], degree),
                        degree + 1,
                        "overfit_risk_control",
                    )
                )
            for model_id, prediction, parameter_count, model_class in models:
                residual = y[test] - prediction
                chi2_values = (residual / sigma[test]) ** 2
                rows.append(
                    {
                        "Dataset": "SOURCE_SPLIT_A2_LOCKED_PREFLIGHT",
                        "SigmaRoute": sigma_route,
                        "ValidationMode": "leave_one_out" if fold_id.startswith("loo") else "blocked_split",
                        "FoldID": fold_id,
                        "ModelID": model_id,
                        "ModelClass": model_class,
                        "ParameterCount": parameter_count,
                        "TrainN": int(train.sum()),
                        "TestN": int(test.sum()),
                        "TestGridIndices": ";".join(str(int(v)) for v in data.loc[test, "GridIndex"]),
                        "TestChi2": float(np.sum(chi2_values)),
                        "TestMeanChi2": float(np.mean(chi2_values)),
                        "TestMeanAbsResidual": float(np.mean(np.abs(residual))),
                        "ClaimBoundary": "a2_polynomial_cv_no_measurement_validation",
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
                "ClaimBoundary": "a2_polynomial_cv_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)

    comparison_rows = []
    for (sigma_route, validation_mode), group in summary.groupby(["SigmaRoute", "ValidationMode"], sort=False):
        a2_row = group[group["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")].iloc[0]
        unit_row = group[group["ModelID"].eq("K2_UNIT_LOCKED_RHO4")].iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        best_poly = group[group["ModelID"].str.startswith("POLY")].sort_values("TotalTestChi2").iloc[0]
        comparison_rows.append(
            {
                "SigmaRoute": sigma_route,
                "ValidationMode": validation_mode,
                "ModelID": "A2_CV_COMPARISON",
                "Folds": int(a2_row["Folds"]),
                "TotalTestN": int(a2_row["TotalTestN"]),
                "A2TotalTestChi2": float(a2_row["TotalTestChi2"]),
                "K2UnitTotalTestChi2": float(unit_row["TotalTestChi2"]),
                "K1TotalTestChi2": float(k1_row["TotalTestChi2"]),
                "BestPolyModel": best_poly["ModelID"],
                "BestPolyTotalTestChi2": float(best_poly["TotalTestChi2"]),
                "DeltaChi2_A2_minus_K1": float(a2_row["TotalTestChi2"] - k1_row["TotalTestChi2"]),
                "DeltaChi2_A2_minus_K2Unit": float(a2_row["TotalTestChi2"] - unit_row["TotalTestChi2"]),
                "DeltaChi2_A2_minus_BestPoly": float(a2_row["TotalTestChi2"] - best_poly["TotalTestChi2"]),
                "A2ImprovesOverK1": bool(a2_row["TotalTestChi2"] < k1_row["TotalTestChi2"]),
                "A2ImprovesOverK2Unit": bool(a2_row["TotalTestChi2"] < unit_row["TotalTestChi2"]),
                "A2BeatsBestPoly": bool(a2_row["TotalTestChi2"] < best_poly["TotalTestChi2"]),
                "ClaimBoundary": "a2_polynomial_cv_no_measurement_validation",
            }
        )

    summary = pd.concat([summary, pd.DataFrame(comparison_rows)], ignore_index=True, sort=False)
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
