#!/usr/bin/env python3
"""Stress-test the A2 projection-gated V3 candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
PRED = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"

OUT = EVIDENCE / "a2_v3_stress_test.csv"
OUT_SUMMARY = EVIDENCE / "a2_v3_stress_test_summary.csv"


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def chi2(y: np.ndarray, pred: np.ndarray, cov: np.ndarray) -> float:
    residual = y - pred
    return float(residual.T @ np.linalg.solve(cov, residual))


def subset_cov(cov: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return cov[np.ix_(mask, mask)] + np.eye(int(mask.sum())) * 1e-12


def masks(data: pd.DataFrame) -> dict[str, np.ndarray]:
    x = data["x_coordinate"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()
    states = data["ProjectionState"].astype(str)
    return {
        "all_rows": np.ones(len(data), dtype=bool),
        "leave_out_grid_0": data["GridIndex"].to_numpy(int) != 0,
        "leave_out_grid_1": data["GridIndex"].to_numpy(int) != 1,
        "leave_out_grid_2": data["GridIndex"].to_numpy(int) != 2,
        "leave_out_grid_3": data["GridIndex"].to_numpy(int) != 3,
        "leave_out_grid_4": data["GridIndex"].to_numpy(int) != 4,
        "leave_out_grid_5": data["GridIndex"].to_numpy(int) != 5,
        "leave_out_grid_6": data["GridIndex"].to_numpy(int) != 6,
        "leave_out_grid_8": data["GridIndex"].to_numpy(int) != 8,
        "low_depth": x < 0.5,
        "mid_depth": (x >= 0.5) & (x < 0.75),
        "high_depth": x >= 0.75,
        "sign_stable": stable,
        "sign_unstable": ~stable,
        "active_full_memory": states.eq("SOURCE_ANTI_COHERENT_MEMORY_ACTIVE").to_numpy(),
        "sign_unstable_unit_memory": states.eq("SIGN_UNSTABLE_UNIT_MEMORY").to_numpy(),
    }


def main() -> None:
    vector = pd.read_csv(VECTOR)
    pred = pd.read_csv(PRED)
    data = vector.merge(
        pred[
            [
                "GridIndex",
                "A2ProjectionGatedV3Prediction",
                "A2ProjectionGatedV2Prediction",
                "A2ScalarV1Prediction",
                "ProjectionState",
                "SignStableTemplate",
            ]
        ],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_covariance(COV, grid)
    model_cols = {
        "K1_NO_MEMORY": "K1Response",
        "A2_SCALAR_V1": "A2ScalarV1Prediction",
        "A2_PROJECTION_GATED_V2": "A2ProjectionGatedV2Prediction",
        "A2_PROJECTION_GATED_V3": "A2ProjectionGatedV3Prediction",
    }

    rows = []
    for subset_id, mask in masks(data).items():
        if int(mask.sum()) < 1:
            continue
        y = data.loc[mask, "SourceSplitCandidate"].to_numpy(float)
        cov_s = subset_cov(cov, mask)
        scores = {}
        for model_id, col in model_cols.items():
            pred_s = data.loc[mask, col].to_numpy(float)
            scores[model_id] = chi2(y, pred_s, cov_s)
            rows.append(
                {
                    "StressID": subset_id,
                    "Rows": int(mask.sum()),
                    "ModelID": model_id,
                    "Chi2": scores[model_id],
                    "AIC": scores[model_id],
                    "MeanAbsResidual": float(np.mean(np.abs(y - pred_s))),
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "a2_v3_stress_test_no_measurement_validation",
                }
            )
        rows.append(
            {
                "StressID": subset_id,
                "Rows": int(mask.sum()),
                "ModelID": "V3_COMPARISON",
                "Chi2": scores["A2_PROJECTION_GATED_V3"],
                "AIC": scores["A2_PROJECTION_GATED_V3"],
                "MeanAbsResidual": np.nan,
                "DeltaAIC_V3_minus_K1": scores["A2_PROJECTION_GATED_V3"] - scores["K1_NO_MEMORY"],
                "DeltaAIC_V3_minus_V2": scores["A2_PROJECTION_GATED_V3"] - scores["A2_PROJECTION_GATED_V2"],
                "DeltaAIC_V3_minus_V1": scores["A2_PROJECTION_GATED_V3"] - scores["A2_SCALAR_V1"],
                "V3ImprovesOverK1": scores["A2_PROJECTION_GATED_V3"] < scores["K1_NO_MEMORY"],
                "V3ImprovesOverV2": scores["A2_PROJECTION_GATED_V3"] < scores["A2_PROJECTION_GATED_V2"],
                "V3ImprovesOverV1": scores["A2_PROJECTION_GATED_V3"] < scores["A2_SCALAR_V1"],
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_stress_test_no_measurement_validation",
            }
        )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    comp = detail[detail["ModelID"].eq("V3_COMPARISON")].copy()
    all_row = comp[comp["StressID"].eq("all_rows")].iloc[0]
    loo = comp[comp["StressID"].str.startswith("leave_out")]
    subset = comp[~comp["StressID"].str.startswith("leave_out") & ~comp["StressID"].eq("all_rows")]
    summary = pd.DataFrame(
        [
            {
                "StressAuditID": "A2_V3_STRESS_TEST_V1",
                "StressComparisons": len(comp),
                "AllRowsDeltaAIC_V3_minus_K1": all_row["DeltaAIC_V3_minus_K1"],
                "AllRowsDeltaAIC_V3_minus_V2": all_row["DeltaAIC_V3_minus_V2"],
                "LeaveOneOutFolds": len(loo),
                "LeaveOneOutV3BeatsK1": int(loo["V3ImprovesOverK1"].astype(bool).sum()),
                "LeaveOneOutV3BeatsV2": int(loo["V3ImprovesOverV2"].astype(bool).sum()),
                "SubsetFolds": len(subset),
                "SubsetV3BeatsK1": int(subset["V3ImprovesOverK1"].astype(bool).sum()),
                "SubsetV3BeatsV2": int(subset["V3ImprovesOverV2"].astype(bool).sum()),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "A2_V3_STRESS_SUPPORTIVE_BUT_WEAK"
                    if bool(all_row["V3ImprovesOverK1"]) and int(loo["V3ImprovesOverK1"].astype(bool).sum()) >= 4
                    else "A2_V3_STRESS_FRAGILE"
                ),
                "StrongestAllowedClaim": "A2 v3 stress test checks whether the K1 advantage survives simple data cuts",
                "ClaimBoundary": "a2_v3_stress_test_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
