#!/usr/bin/env python3
"""Run A2 projection-gated V3 candidate selected by ablation."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EVIDENCE = ROOT / "evidence"
POLICY = ROOT / "frozen" / "a2_projection_gate_policy_v3_candidate.yaml"
VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
META = EVIDENCE / "source_split_coordinate_native_target.csv"
V2 = EVIDENCE / "a2_projection_gated_candidate_prediction.csv"

OUT_PRED = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"
OUT_SCORE = EVIDENCE / "a2_projection_gated_v3_candidate_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "a2_projection_gated_v3_candidate_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def v3_prediction(row: pd.Series) -> tuple[float, str, float, str]:
    x = float(row["x_coordinate"])
    k1 = float(row["K1Response"])
    stable = truthy(row["SignStableTemplate"])
    same = truthy(row["SNBAOSameSign"])
    if abs(k1) < 0.001:
        return k1, "K1_NULL_SUPPRESSED", 1.0, "near-null K1 does not get sign-inventing amplification"
    if x < 0.5:
        return k1, "LOW_DEPTH_BASELINE", 1.0, "projection memory remains weak at low depth"
    if not stable:
        multiplier = float(w_k2_locked([x], rho=4.0)[0])
        return k1 * multiplier, "SIGN_UNSTABLE_UNIT_MEMORY", multiplier, "sign-unstable rows carry unit memory without A_tau amplification"
    if same:
        return k1, "SOURCE_COHERENT_COMMON_MODE", 1.0, "same-direction SN/BAO response is common-mode"
    multiplier = float(2.0 * w_k2_locked([x], rho=4.0)[0])
    return k1 * multiplier, "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE", multiplier, "opposed SN/BAO response is source-split memory-active"


def main() -> None:
    vector = pd.read_csv(VECTOR)
    meta = pd.read_csv(META)[["GridIndex", "SignStableTemplate", "SNBAOSameSign"]]
    v2 = pd.read_csv(V2)[["GridIndex", "A2ProjectionGatedPrediction"]]
    data = (
        vector.merge(meta, on="GridIndex", how="left")
        .merge(v2, on="GridIndex", how="left")
        .sort_values("GridIndex")
    )
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_covariance(COV, grid)
    rows = []
    for _, row in data.iterrows():
        pred, state, multiplier, reason = v3_prediction(row)
        rows.append(
            {
                "PredictionID": "A2_PROJECTION_GATE_POLICY_V3_CANDIDATE",
                "PolicyFile": str(POLICY.relative_to(ROOT)),
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "K1Response": row["K1Response"],
                "A2ScalarV1Prediction": row["K2LockedA2Prediction"],
                "A2ProjectionGatedV2Prediction": row["A2ProjectionGatedPrediction"],
                "A2ProjectionGatedV3Prediction": pred,
                "ProjectionState": state,
                "ProjectionMultiplier": multiplier,
                "SignStableTemplate": row["SignStableTemplate"],
                "SNBAOSameSign": row["SNBAOSameSign"],
                "RuleReason": reason,
                "A_tau": 2.0,
                "Rho": 4.0,
                "P": 3,
                "KernelChanged": False,
                "K1Refit": False,
                "TargetSignUsedForGate": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gate_v3_candidate_no_measurement_validation",
            }
        )
    pred_df = pd.DataFrame(rows)
    pred_df.to_csv(OUT_PRED, index=False)

    y = data["SourceSplitCandidate"].to_numpy(float)
    x = data["x_coordinate"].to_numpy(float)
    models = [
        ("K1_NO_MEMORY", data["K1Response"].to_numpy(float), 0, "fair_null"),
        ("A2_SCALAR_V1_LOCKED", data["K2LockedA2Prediction"].to_numpy(float), 0, "locked_prediction_v1"),
        ("A2_PROJECTION_GATED_V2", data["A2ProjectionGatedPrediction"].to_numpy(float), 0, "projection_gated_v2"),
        ("A2_PROJECTION_GATED_V3", pred_df["A2ProjectionGatedV3Prediction"].to_numpy(float), 0, "projection_gated_v3_candidate"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        models.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))

    scores = []
    for model_id, pred, k, model_class in models:
        c2 = chi2(y, pred, cov)
        scores.append(
            {
                "CandidateID": "A2_PROJECTION_GATE_POLICY_V3_CANDIDATE",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gate_v3_candidate_no_measurement_validation",
            }
        )
    score = pd.DataFrame(scores)
    score.to_csv(OUT_SCORE, index=False)

    k1_aic = float(score.loc[score["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    v1_aic = float(score.loc[score["ModelID"].eq("A2_SCALAR_V1_LOCKED"), "AIC"].iloc[0])
    v2_aic = float(score.loc[score["ModelID"].eq("A2_PROJECTION_GATED_V2"), "AIC"].iloc[0])
    v3_aic = float(score.loc[score["ModelID"].eq("A2_PROJECTION_GATED_V3"), "AIC"].iloc[0])
    poly_aic = float(score[score["ModelID"].str.startswith("POLY")]["AIC"].min())
    best = score.loc[score["AIC"].idxmin()]
    summary = pd.DataFrame(
        [
            {
                "CandidateID": "A2_PROJECTION_GATE_POLICY_V3_CANDIDATE",
                "PolicyFile": str(POLICY.relative_to(ROOT)),
                "Rows": len(pred_df),
                "SignUnstableUnitRows": int(pred_df["ProjectionState"].eq("SIGN_UNSTABLE_UNIT_MEMORY").sum()),
                "ActiveFullMemoryRows": int(pred_df["ProjectionState"].eq("SOURCE_ANTI_COHERENT_MEMORY_ACTIVE").sum()),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "A2ScalarV1AIC": v1_aic,
                "A2ProjectionGatedV2AIC": v2_aic,
                "A2ProjectionGatedV3AIC": v3_aic,
                "BestPolyAIC": poly_aic,
                "DeltaAIC_V3_minus_V2": v3_aic - v2_aic,
                "DeltaAIC_V3_minus_V1": v3_aic - v1_aic,
                "DeltaAIC_V3_minus_K1": v3_aic - k1_aic,
                "DeltaAIC_V3_minus_BestPoly": v3_aic - poly_aic,
                "V3ImprovesOverV2": v3_aic < v2_aic,
                "V3ImprovesOverV1": v3_aic < v1_aic,
                "V3ImprovesOverK1": v3_aic < k1_aic,
                "V3BeatsBestPoly": v3_aic < poly_aic,
                "KernelChanged": False,
                "Rho": 4.0,
                "P": 3,
                "A_tau": 2.0,
                "K1Refit": False,
                "TargetSignUsedForGate": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "A2_V3_CANDIDATE_SUPPORTIVE_AGAINST_K1_NOT_POLY"
                    if v3_aic < k1_aic and v3_aic >= poly_aic
                    else "A2_V3_CANDIDATE_SUPPORTIVE_PREFLIGHT"
                    if v3_aic < k1_aic and v3_aic < poly_aic
                    else "A2_V3_CANDIDATE_NOT_SUPPORTIVE"
                ),
                "StrongestAllowedClaim": "A2 v3 candidate improves the projection-gated structure without changing locked amplitude/kernel parameters",
                "PrimaryResidualRisk": "v3 is ablation-derived and must be independently stress-tested before any promotion",
                "ClaimBoundary": "a2_projection_gate_v3_candidate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_PRED}")
    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
