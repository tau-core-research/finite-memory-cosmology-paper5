#!/usr/bin/env python3
"""Ablate A2 projection gates without fitting amplitudes."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
BASE_PRED = EVIDENCE / "a2_projection_gated_candidate_prediction.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"

OUT = EVIDENCE / "a2_projection_gate_ablation.csv"
OUT_SUMMARY = EVIDENCE / "a2_projection_gate_ablation_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def w_locked(x: float) -> float:
    return 1.0 + 4.0 * float(x) ** 3


def pred_for_variant(row: pd.Series, variant: str) -> tuple[float, str]:
    k1 = float(row["K1Response"])
    x = float(row["x_coordinate"])
    stable = truthy(row["SignStableTemplate"])
    same = truthy(row["SNBAOSameSign"])
    scalar = float(row["K2LockedA2Prediction"])
    unit = k1 * w_locked(x)
    active = 2.0 * unit

    if variant == "V2_BASE":
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "V1_SCALAR":
        return scalar, "all_rows_memory_active"
    if variant == "NO_LOW_DEPTH_SUPPRESSION":
        if x < 0.5 and stable and not same:
            return active, "low_depth_anti_coherent_active"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "ALLOW_COMMON_MODE_UNIT":
        if same and stable and abs(k1) >= 0.001 and x >= 0.5:
            return unit, "source_coherent_unit_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "ALLOW_COMMON_MODE_FULL":
        if same and stable and abs(k1) >= 0.001 and x >= 0.5:
            return active, "source_coherent_full_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "SIGN_UNSTABLE_UNIT":
        if not stable and abs(k1) >= 0.001 and x >= 0.5:
            return unit, "sign_unstable_unit_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "SIGN_UNSTABLE_FULL":
        if not stable and abs(k1) >= 0.001 and x >= 0.5:
            return active, "sign_unstable_full_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "ANTI_COHERENT_UNIT":
        if stable and not same and abs(k1) >= 0.001 and x >= 0.5:
            return unit, "anti_coherent_unit_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    if variant == "NO_K1_NULL_SUPPRESSION":
        if abs(k1) < 0.001 and stable and x >= 0.5:
            return active, "k1_null_full_memory"
        return float(row["A2ProjectionGatedPrediction"]), str(row["ProjectionState"])
    raise ValueError(f"unknown variant: {variant}")


def chi2(y: np.ndarray, pred: np.ndarray, cov: np.ndarray) -> float:
    residual = y - pred
    return float(residual.T @ np.linalg.solve(cov, residual))


def main() -> None:
    vector = pd.read_csv(VECTOR)
    pred = pd.read_csv(BASE_PRED)
    data = vector.merge(
        pred[["GridIndex", "A2ProjectionGatedPrediction", "ProjectionState", "SignStableTemplate", "SNBAOSameSign"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    cov = load_covariance(COV, grid)
    y = data["SourceSplitCandidate"].to_numpy(float)

    variants = [
        "V2_BASE",
        "V1_SCALAR",
        "NO_LOW_DEPTH_SUPPRESSION",
        "ALLOW_COMMON_MODE_UNIT",
        "ALLOW_COMMON_MODE_FULL",
        "SIGN_UNSTABLE_UNIT",
        "SIGN_UNSTABLE_FULL",
        "ANTI_COHERENT_UNIT",
        "NO_K1_NULL_SUPPRESSION",
    ]
    rows = []
    pred_rows = []
    for variant in variants:
        values = []
        states = []
        changed = 0
        for _, row in data.iterrows():
            value, state = pred_for_variant(row, variant)
            values.append(value)
            states.append(state)
            if abs(value - float(row["A2ProjectionGatedPrediction"])) > 1e-12:
                changed += 1
            pred_rows.append(
                {
                    "VariantID": variant,
                    "GridIndex": int(row["GridIndex"]),
                    "Prediction": value,
                    "VariantState": state,
                    "ChangedFromV2": abs(value - float(row["A2ProjectionGatedPrediction"])) > 1e-12,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "a2_projection_gate_ablation_no_measurement_validation",
                }
            )
        values_arr = np.asarray(values, dtype=float)
        c2 = chi2(y, values_arr, cov)
        rows.append(
            {
                "VariantID": variant,
                "Rows": len(y),
                "RowsChangedFromV2": changed,
                "Chi2": c2,
                "AIC": c2,
                "MeanAbsResidual": float(np.mean(np.abs(y - values_arr))),
                "KernelChanged": False,
                "Rho": 4.0,
                "P": 3,
                "A_tau": 2.0,
                "K1Refit": False,
                "TargetSignUsedForGate": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_projection_gate_ablation_no_measurement_validation",
            }
        )
    ablation = pd.DataFrame(rows)
    k1_chi2 = chi2(y, data["K1Response"].to_numpy(float), cov)
    best = ablation.loc[ablation["AIC"].idxmin()]
    v2 = ablation[ablation["VariantID"].eq("V2_BASE")].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "A2_PROJECTION_GATE_ABLATION_V1",
                "Variants": len(ablation),
                "BestVariant": best["VariantID"],
                "BestVariantAIC": best["AIC"],
                "V2BaseAIC": v2["AIC"],
                "K1AIC": k1_chi2,
                "DeltaBest_minus_V2": float(best["AIC"] - v2["AIC"]),
                "DeltaBest_minus_K1": float(best["AIC"] - k1_chi2),
                "BestImprovesOverV2": float(best["AIC"]) < float(v2["AIC"]),
                "BestImprovesOverK1": float(best["AIC"]) < k1_chi2,
                "KernelChanged": False,
                "Rho": 4.0,
                "P": 3,
                "A_tau": 2.0,
                "K1Refit": False,
                "TargetSignUsedForGate": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "ABLATION_IDENTIFIES_STRUCTURAL_GATE_CANDIDATE"
                    if float(best["AIC"]) < float(v2["AIC"])
                    else "ABLATION_DOES_NOT_IMPROVE_V2"
                ),
                "StrongestAllowedClaim": "ablation localizes which predeclared projection gates deserve v3 consideration",
                "ClaimBoundary": "a2_projection_gate_ablation_no_measurement_validation",
            }
        ]
    )
    pd.DataFrame(pred_rows).to_csv(EVIDENCE / "a2_projection_gate_ablation_predictions.csv", index=False)
    ablation.to_csv(OUT, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {EVIDENCE / 'a2_projection_gate_ablation_predictions.csv'}")


if __name__ == "__main__":
    main()
