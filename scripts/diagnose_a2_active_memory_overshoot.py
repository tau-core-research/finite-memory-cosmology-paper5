#!/usr/bin/env python3
"""Audit active-memory overshoot in A2 v3.

This separates a locked A_tau=2 failure from a target/covariance/source-branch
normalization issue. It does not alter A_tau, rho, p, K1, or the prediction.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

AUDIT = EVIDENCE / "a2_v3_residual_mechanism_audit.csv"
BASELINE = EVIDENCE / "source_split_likelihood_native_amplitude_gap_audit.csv"
GAIN = EVIDENCE / "tau_gain_stability_summary.csv"
SCALE_COV = EVIDENCE / "source_split_likelihood_native_scale_covariance_summary.csv"

OUT_AUDIT = EVIDENCE / "a2_active_memory_overshoot_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_active_memory_overshoot_summary.csv"


def safe_ratio(num: float, den: float) -> float:
    if abs(den) < 1e-12:
        return float("nan")
    return float(num / den)


def classify(required_a_tau: float, locked_a_tau: float, target_over_v3: float) -> tuple[str, str, str]:
    if not np.isfinite(required_a_tau):
        return (
            "UNDEFINED_REQUIRED_GAIN",
            "required A_tau is undefined because the baseline response is too close to zero",
            "handle in K1-null audit, not active-memory overshoot",
        )
    if required_a_tau < 0:
        return (
            "SIGN_CONVENTION_CONFLICT",
            "target and K1 imply opposite signs for the active-memory channel",
            "audit source-branch sign convention before any rerun",
        )
    if required_a_tau < 0.5 * locked_a_tau and abs(target_over_v3) < 0.5:
        return (
            "LOCKED_A2_OVERSHOOTS_RERUN_TARGET_SCALE",
            "locked A_tau=2 predicts a response larger than the current rerun target scale",
            "test source-branch/covariance normalization before treating this as A_tau evidence",
        )
    if 0.5 * locked_a_tau <= required_a_tau <= 1.5 * locked_a_tau:
        return (
            "LOCKED_A2_SCALE_COMPATIBLE",
            "target-implied gain is near the locked A_tau=2 scale",
            "retain as active-memory support under preflight boundary",
        )
    return (
        "ACTIVE_MEMORY_SCALE_MISMATCH",
        "target-implied gain differs materially from the locked A_tau=2 scale",
        "separate target-scale policy from A2 amplitude before rerun",
    )


def main() -> None:
    audit = pd.read_csv(AUDIT)
    amp = pd.read_csv(BASELINE)
    gain = pd.read_csv(GAIN)
    scale = pd.read_csv(SCALE_COV)

    active = audit[audit["ProjectionState"].eq("SOURCE_ANTI_COHERENT_MEMORY_ACTIVE")].copy()
    data = active.merge(
        amp[["GridIndex", "TargetOverK1", "TargetOverK2Rho4", "K2OverK1", "DominanceNote"]],
        on="GridIndex",
        how="left",
    )

    rows = []
    for _, row in data.iterrows():
        target = float(row["SourceSplitCandidate"])
        k1 = float(row["K1Response"])
        v3 = float(row["A2ProjectionGatedV3Prediction"])
        locked_multiplier = float(row["ProjectionMultiplier"])
        w_locked = locked_multiplier / 2.0
        required_multiplier = safe_ratio(target, k1)
        required_a_tau = safe_ratio(required_multiplier, w_locked)
        target_over_v3 = safe_ratio(target, v3)
        class_id, interpretation, next_check = classify(required_a_tau, 2.0, target_over_v3)
        rows.append(
            {
                "AuditID": "A2_ACTIVE_MEMORY_OVERSHOOT_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "SourceSplitCandidate": target,
                "K1Response": k1,
                "A2ProjectionGatedV3Prediction": v3,
                "LockedProjectionMultiplier": locked_multiplier,
                "LockedW": w_locked,
                "LockedATau": 2.0,
                "TargetRequiredMultiplierOverK1": required_multiplier,
                "TargetImpliedATau": required_a_tau,
                "TargetOverA2V3": target_over_v3,
                "OvershootFactorA2OverTarget": safe_ratio(v3, target),
                "K1Chi2Contribution": row["K1Chi2Contribution"],
                "V3Chi2Contribution": row["V3Chi2Contribution"],
                "DeltaChi2_V3_minus_K1": row["DeltaChi2_V3_minus_K1"],
                "DominanceNote": row["DominanceNote"],
                "OvershootClass": class_id,
                "Interpretation": interpretation,
                "RequiredNextCheck": next_check,
                "KernelChanged": False,
                "Rho": 4.0,
                "P": 3,
                "A_tau_changed": False,
                "K1Refit": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_active_memory_overshoot_audit_no_measurement_validation",
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUT_AUDIT, index=False)

    mid_high = gain[gain["Subset"].eq("mid_high_depth")].iloc[0]
    high = gain[gain["Subset"].eq("high_depth")].iloc[0]
    scale_support = scale[scale["CovarianceCase"].eq("diag_target_fraction_floor_25pct")].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "A2_ACTIVE_MEMORY_OVERSHOOT_AUDIT_SUMMARY",
                "ActiveMemoryRows": len(out),
                "OvershootRows": int(out["OvershootClass"].eq("LOCKED_A2_OVERSHOOTS_RERUN_TARGET_SCALE").sum()),
                "MeanTargetImpliedATau": float(out["TargetImpliedATau"].mean()) if len(out) else float("nan"),
                "MinTargetImpliedATau": float(out["TargetImpliedATau"].min()) if len(out) else float("nan"),
                "MaxTargetImpliedATau": float(out["TargetImpliedATau"].max()) if len(out) else float("nan"),
                "LockedATau": 2.0,
                "MidHighCommonGain": mid_high["FittedCommonGain"],
                "HighDepthCommonGain": high["FittedCommonGain"],
                "TargetFraction25pctK2ImprovesOverK1": scale_support["K2ImprovesOverK1"],
                "TargetFraction25pctK2BeatsBestPoly": scale_support["K2BeatsBestPoly"],
                "AllowedToChangeATau": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "ACTIVE_MEMORY_OVERSHOOT_POINTS_TO_TARGET_SCALE_NOT_ATAU_REFIT",
                "StrongestAllowedClaim": "active-memory overshoot is localized and tied to rerun target-scale normalization",
                "RequiredNextCheck": "run source-branch/covariance normalization audit before any A2 rerun; keep A_tau=2 locked",
                "ClaimBoundary": "a2_active_memory_overshoot_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
