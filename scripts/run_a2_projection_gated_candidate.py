#!/usr/bin/env python3
"""Run the predeclared A2 projection-gated candidate.

The V2 policy changes only the discrete Tau Core projection state. It does not
change A_tau, rho, p, K1, or select gates from target residual signs.
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

EVIDENCE = ROOT / "evidence"
FROZEN = ROOT / "frozen"

POLICY = FROZEN / "a2_projection_gate_policy_v2.yaml"
VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
TARGET_META = EVIDENCE / "source_split_coordinate_native_target.csv"

OUT_PRED = EVIDENCE / "a2_projection_gated_candidate_prediction.csv"
OUT_SCORE = EVIDENCE / "a2_projection_gated_candidate_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "a2_projection_gated_candidate_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_candidate_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path)
    rows = rows.set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def projection_state(x: float, k1: float, sign_stable: bool, sn_bao_same_sign: bool) -> tuple[str, float, str]:
    if abs(float(k1)) < 0.001:
        return "K1_NULL_SUPPRESSED", 1.0, "near-null K1 does not get sign-inventing amplification"
    if float(x) < 0.5:
        return "LOW_DEPTH_BASELINE", 1.0, "projection memory remains weak at low depth"
    if not sign_stable:
        return "SIGN_UNSTABLE_SUPPRESSED", 1.0, "unstable reconstruction sign is not forced by A2"
    if sn_bao_same_sign:
        return "SOURCE_COHERENT_COMMON_MODE", 1.0, "same-direction SN/BAO response is common-mode"
    return (
        "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE",
        float(2.0 * w_k2_locked([x], rho=4.0)[0]),
        "opposed SN/BAO response is the source-split memory-active channel",
    )


def positive_definite(cov: np.ndarray) -> tuple[bool, float, float]:
    eig = np.linalg.eigvalsh(np.asarray(cov, dtype=float))
    return bool(float(np.min(eig)) > 0.0), float(np.min(eig)), float(np.max(eig))


def main() -> None:
    candidate = pd.read_csv(VECTOR).sort_values("GridIndex")
    meta = pd.read_csv(TARGET_META)[["GridIndex", "SignStableTemplate", "SNBAOSameSign"]]
    data = candidate.merge(meta, on="GridIndex", how="left").sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_candidate_covariance(COV, grid)
    pd_ok, eig_min, eig_max = positive_definite(cov)

    rows: list[dict[str, object]] = []
    for _, row in data.iterrows():
        state, multiplier, reason = projection_state(
            float(row["x_coordinate"]),
            float(row["K1Response"]),
            truthy(row["SignStableTemplate"]),
            truthy(row["SNBAOSameSign"]),
        )
        prediction = float(row["K1Response"]) * multiplier
        rows.append(
            {
                "PredictionID": "A2_PROJECTION_GATED_POLICY_V2",
                "PolicyFile": str(POLICY.relative_to(ROOT)),
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "K1Response": row["K1Response"],
                "A2ScalarV1Prediction": row["K2LockedA2Prediction"],
                "A2ProjectionGatedPrediction": prediction,
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
                "ClaimBoundary": "projection_gated_a2_candidate_no_measurement_validation",
            }
        )
    pred_df = pd.DataFrame(rows)
    pred_df.to_csv(OUT_PRED, index=False)

    y = data["SourceSplitCandidate"].to_numpy(float)
    x = data["x_coordinate"].to_numpy(float)
    models = [
        ("K1_NO_MEMORY", data["K1Response"].to_numpy(float), 0, "fair_null"),
        ("A2_SCALAR_V1_LOCKED", data["K2LockedA2Prediction"].to_numpy(float), 0, "locked_prediction_v1"),
        ("A2_PROJECTION_GATED_V2", pred_df["A2ProjectionGatedPrediction"].to_numpy(float), 0, "projection_gated_candidate"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        models.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))

    score_rows = []
    for model_id, model_pred, k, model_class in models:
        c2 = chi2(y, model_pred, cov)
        score_rows.append(
            {
                "CandidateID": "A2_PROJECTION_GATE_POLICY_V2_RERUN",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "MeanAbsResidual": float(np.mean(np.abs(y - model_pred))),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "projection_gated_a2_candidate_no_measurement_validation",
            }
        )
    score = pd.DataFrame(score_rows)
    score.to_csv(OUT_SCORE, index=False)

    k1_aic = float(score.loc[score["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    v1_aic = float(score.loc[score["ModelID"].eq("A2_SCALAR_V1_LOCKED"), "AIC"].iloc[0])
    v2_aic = float(score.loc[score["ModelID"].eq("A2_PROJECTION_GATED_V2"), "AIC"].iloc[0])
    best_poly_aic = float(score[score["ModelID"].str.startswith("POLY")]["AIC"].min())
    best = score.loc[score["AIC"].idxmin()]
    active = int(pred_df["ProjectionState"].eq("SOURCE_ANTI_COHERENT_MEMORY_ACTIVE").sum())
    suppressed = len(pred_df) - active
    summary = pd.DataFrame(
        [
            {
                "CandidateID": "A2_PROJECTION_GATE_POLICY_V2_RERUN",
                "PolicyFile": str(POLICY.relative_to(ROOT)),
                "Rows": len(pred_df),
                "ActiveMemoryRows": active,
                "SuppressedOrBaselineRows": suppressed,
                "CovariancePositiveDefinite": pd_ok,
                "CovarianceMinEigenvalue": eig_min,
                "CovarianceMaxEigenvalue": eig_max,
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "A2ScalarV1AIC": v1_aic,
                "A2ProjectionGatedV2AIC": v2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_V2_minus_V1": v2_aic - v1_aic,
                "DeltaAIC_V2_minus_K1": v2_aic - k1_aic,
                "DeltaAIC_V2_minus_BestPoly": v2_aic - best_poly_aic,
                "V2ImprovesOverV1": v2_aic < v1_aic,
                "V2ImprovesOverK1": v2_aic < k1_aic,
                "V2BeatsBestPoly": v2_aic < best_poly_aic,
                "KernelChanged": False,
                "Rho": 4.0,
                "P": 3,
                "A_tau": 2.0,
                "K1Refit": False,
                "TargetSignUsedForGate": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "A2_V2_STRUCTURAL_REFINEMENT_SUPPORTIVE_PREFLIGHT"
                    if v2_aic < v1_aic and v2_aic < k1_aic
                    else "A2_V2_IMPROVES_V1_BUT_NOT_NULLS"
                    if v2_aic < v1_aic
                    else "A2_V2_NOT_SUPPORTIVE_ON_RERUN_CANDIDATE"
                ),
                "StrongestAllowedClaim": "projection-gated A2 v2 tests a non-fitted Tau Core structural refinement",
                "PrimaryResidualRisk": "projection gates are theory-declared but still require independent validation and final covariance route",
                "ClaimBoundary": "projection_gated_a2_candidate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_PRED}")
    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
