#!/usr/bin/env python3
"""Cross-validate A2 V3 candidate against polynomial controls."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
PRED = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"

OUT = EVIDENCE / "a2_v3_polynomial_cv.csv"
OUT_SUMMARY = EVIDENCE / "a2_v3_polynomial_cv_summary.csv"


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def fold_masks(n: int, x: np.ndarray) -> dict[str, np.ndarray]:
    masks: dict[str, np.ndarray] = {}
    for idx in range(n):
        test = np.zeros(n, dtype=bool)
        test[idx] = True
        masks[f"loo_{idx}"] = test
    masks["low_depth_block"] = x < 0.5
    masks["mid_depth_block"] = (x >= 0.5) & (x < 0.75)
    masks["high_depth_block"] = x >= 0.75
    return masks


def weighted_poly_predict(x_train, y_train, sigma_train, x_test, degree: int) -> np.ndarray:
    weights = np.where(sigma_train > 0.0, 1.0 / sigma_train, 0.0)
    coeff = np.polyfit(x_train, y_train, degree, w=weights)
    return np.polyval(coeff, x_test)


def main() -> None:
    vector = pd.read_csv(VECTOR)
    pred = pd.read_csv(PRED)
    data = vector.merge(
        pred[["GridIndex", "A2ProjectionGatedV3Prediction", "A2ProjectionGatedV2Prediction", "A2ScalarV1Prediction"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_covariance(COV, grid)
    sigma = np.sqrt(np.diag(cov))
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitCandidate"].to_numpy(float)
    rows = []
    for fold_id, test in fold_masks(len(data), x).items():
        train = ~test
        if int(test.sum()) < 1 or int(train.sum()) < 5:
            continue
        models: list[tuple[str, np.ndarray, int, str]] = [
            ("K1_NO_MEMORY", data.loc[test, "K1Response"].to_numpy(float), 0, "fair_null"),
            ("A2_SCALAR_V1", data.loc[test, "A2ScalarV1Prediction"].to_numpy(float), 0, "locked_v1"),
            ("A2_PROJECTION_GATED_V2", data.loc[test, "A2ProjectionGatedV2Prediction"].to_numpy(float), 0, "gated_v2"),
            ("A2_PROJECTION_GATED_V3", data.loc[test, "A2ProjectionGatedV3Prediction"].to_numpy(float), 0, "gated_v3_candidate"),
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
        for model_id, model_pred, k, model_class in models:
            residual = y[test] - model_pred
            chi2_values = (residual / sigma[test]) ** 2
            rows.append(
                {
                    "FoldID": fold_id,
                    "ValidationMode": "leave_one_out" if fold_id.startswith("loo") else "blocked_split",
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "ParameterCount": k,
                    "TrainN": int(train.sum()),
                    "TestN": int(test.sum()),
                    "TestGridIndices": ";".join(str(int(v)) for v in data.loc[test, "GridIndex"]),
                    "TestChi2": float(np.sum(chi2_values)),
                    "TestMeanChi2": float(np.mean(chi2_values)),
                    "TestMeanAbsResidual": float(np.mean(np.abs(residual))),
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "a2_v3_polynomial_cv_no_measurement_validation",
                }
            )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (mode, model_id), group in detail.groupby(["ValidationMode", "ModelID"], sort=False):
        summary_rows.append(
            {
                "ValidationMode": mode,
                "ModelID": model_id,
                "Folds": len(group),
                "TotalTestN": int(group["TestN"].sum()),
                "TotalTestChi2": float(group["TestChi2"].sum()),
                "MeanFoldChi2": float(group["TestChi2"].mean()),
                "MeanAbsResidual": float(group["TestMeanAbsResidual"].mean()),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_polynomial_cv_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    comparisons = []
    for mode, group in summary.groupby("ValidationMode", sort=False):
        v3 = group[group["ModelID"].eq("A2_PROJECTION_GATED_V3")].iloc[0]
        k1 = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        v2 = group[group["ModelID"].eq("A2_PROJECTION_GATED_V2")].iloc[0]
        best_poly = group[group["ModelID"].str.startswith("POLY")].sort_values("TotalTestChi2").iloc[0]
        comparisons.append(
            {
                "ValidationMode": mode,
                "ModelID": "V3_CV_COMPARISON",
                "Folds": int(v3["Folds"]),
                "TotalTestN": int(v3["TotalTestN"]),
                "V3TotalTestChi2": float(v3["TotalTestChi2"]),
                "K1TotalTestChi2": float(k1["TotalTestChi2"]),
                "V2TotalTestChi2": float(v2["TotalTestChi2"]),
                "BestPolyModel": best_poly["ModelID"],
                "BestPolyTotalTestChi2": float(best_poly["TotalTestChi2"]),
                "DeltaChi2_V3_minus_K1": float(v3["TotalTestChi2"] - k1["TotalTestChi2"]),
                "DeltaChi2_V3_minus_V2": float(v3["TotalTestChi2"] - v2["TotalTestChi2"]),
                "DeltaChi2_V3_minus_BestPoly": float(v3["TotalTestChi2"] - best_poly["TotalTestChi2"]),
                "V3ImprovesOverK1": bool(v3["TotalTestChi2"] < k1["TotalTestChi2"]),
                "V3ImprovesOverV2": bool(v3["TotalTestChi2"] < v2["TotalTestChi2"]),
                "V3BeatsBestPoly": bool(v3["TotalTestChi2"] < best_poly["TotalTestChi2"]),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_polynomial_cv_no_measurement_validation",
            }
        )
    summary = pd.concat([summary, pd.DataFrame(comparisons)], ignore_index=True, sort=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
