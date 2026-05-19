#!/usr/bin/env python3
"""Row-level tension audit for A2 projection-gated V2."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
PRED = EVIDENCE / "a2_projection_gated_candidate_prediction.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"

OUT_AUDIT = EVIDENCE / "a2_projection_gated_row_tension.csv"
OUT_SUMMARY = EVIDENCE / "a2_projection_gated_row_tension_summary.csv"


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def classify(row: pd.Series) -> str:
    target = float(row["SourceSplitCandidate"])
    v2 = float(row["A2ProjectionGatedPrediction"])
    k1 = float(row["K1Response"])
    if np.sign(v2) != np.sign(target) and abs(target) > 1e-12 and abs(v2) > 1e-12:
        return "V2_SIGN_MISMATCH"
    if abs(v2 - target) > abs(k1 - target):
        return "V2_WORSE_THAN_K1"
    if str(row["ProjectionState"]) == "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE" and abs(v2) > abs(target):
        return "ACTIVE_MEMORY_OVERSHOOT"
    if str(row["ProjectionState"]).endswith("SUPPRESSED") and abs(k1 - target) > 1.0:
        return "SUPPRESSION_LEAVES_LARGE_RESIDUAL"
    return "V2_ROW_NON_DOMINANT_TENSION"


def main() -> None:
    vector = pd.read_csv(VECTOR)
    pred = pd.read_csv(PRED)
    data = vector.merge(
        pred[
            [
                "GridIndex",
                "A2ScalarV1Prediction",
                "A2ProjectionGatedPrediction",
                "ProjectionState",
                "ProjectionMultiplier",
                "RuleReason",
            ]
        ],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_covariance(COV, grid)
    sigma = np.sqrt(np.diag(cov))

    rows = []
    for i, row in data.reset_index(drop=True).iterrows():
        target = float(row["SourceSplitCandidate"])
        k1 = float(row["K1Response"])
        v1 = float(row["A2ScalarV1Prediction"])
        v2 = float(row["A2ProjectionGatedPrediction"])
        sigma_i = float(sigma[i])
        k1_resid = target - k1
        v1_resid = target - v1
        v2_resid = target - v2
        rows.append(
            {
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "SourceSplitCandidate": target,
                "K1Response": k1,
                "A2ScalarV1Prediction": v1,
                "A2ProjectionGatedPrediction": v2,
                "ProjectionState": row["ProjectionState"],
                "ProjectionMultiplier": row["ProjectionMultiplier"],
                "SigmaDiag": sigma_i,
                "K1Residual": k1_resid,
                "V1Residual": v1_resid,
                "V2Residual": v2_resid,
                "AbsK1Residual": abs(k1_resid),
                "AbsV1Residual": abs(v1_resid),
                "AbsV2Residual": abs(v2_resid),
                "K1Chi2DiagContribution": (k1_resid / sigma_i) ** 2,
                "V1Chi2DiagContribution": (v1_resid / sigma_i) ** 2,
                "V2Chi2DiagContribution": (v2_resid / sigma_i) ** 2,
                "V2ImprovesOverV1Row": abs(v2_resid) < abs(v1_resid),
                "V2ImprovesOverK1Row": abs(v2_resid) < abs(k1_resid),
                "TensionType": classify(row),
                "RuleReason": row["RuleReason"],
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gated_row_tension_no_measurement_validation",
            }
        )
    audit = pd.DataFrame(rows)
    audit["ContributionRankV2"] = audit["V2Chi2DiagContribution"].rank(method="first", ascending=False).astype(int)
    audit.sort_values("GridIndex").to_csv(OUT_AUDIT, index=False)

    by_state = (
        audit.groupby("ProjectionState", dropna=False)
        .agg(
            Rows=("GridIndex", "count"),
            V2ImprovesOverV1Rows=("V2ImprovesOverV1Row", "sum"),
            V2ImprovesOverK1Rows=("V2ImprovesOverK1Row", "sum"),
            MeanAbsV2Residual=("AbsV2Residual", "mean"),
            SumV2Chi2Diag=("V2Chi2DiagContribution", "sum"),
        )
        .reset_index()
    )
    summary_rows = []
    for _, row in by_state.iterrows():
        summary_rows.append(
            {
                "SummaryID": "A2_PROJECTION_GATED_ROW_TENSION_BY_STATE",
                **row.to_dict(),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gated_row_tension_no_measurement_validation",
            }
        )
    worst = audit.sort_values("V2Chi2DiagContribution", ascending=False).head(3)
    for _, row in worst.iterrows():
        summary_rows.append(
            {
                "SummaryID": "A2_PROJECTION_GATED_WORST_ROWS",
                "ProjectionState": row["ProjectionState"],
                "Rows": 1,
                "V2ImprovesOverV1Rows": int(row["V2ImprovesOverV1Row"]),
                "V2ImprovesOverK1Rows": int(row["V2ImprovesOverK1Row"]),
                "MeanAbsV2Residual": row["AbsV2Residual"],
                "SumV2Chi2Diag": row["V2Chi2DiagContribution"],
                "WorstGridIndex": row["GridIndex"],
                "TensionType": row["TensionType"],
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gated_row_tension_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
