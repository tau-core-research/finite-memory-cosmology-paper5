#!/usr/bin/env python3
"""Diagnose the mixed/weakening locked-A2 rerun candidate.

This diagnostic decomposes the candidate y_split/C_split rerun at row level.
It does not alter A2, K1, the covariance, or any model score.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
SCORE = EVIDENCE / "likelihood_native_rerun_candidate_scorecard.csv"
SUMMARY_IN = EVIDENCE / "likelihood_native_rerun_candidate_summary.csv"

OUT_AUDIT = EVIDENCE / "likelihood_native_rerun_weakening_audit.csv"
OUT_SUMMARY = EVIDENCE / "likelihood_native_rerun_weakening_summary.csv"


def depth_zone(x: float) -> str:
    if x < 0.5:
        return "low_depth"
    if x < 0.8:
        return "mid_depth"
    return "high_depth"


def signed_class(value: float) -> str:
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def main() -> None:
    vector = pd.read_csv(VECTOR)
    score = pd.read_csv(SCORE)
    rerun = pd.read_csv(SUMMARY_IN).iloc[0]

    y = vector["SourceSplitCandidate"].to_numpy(float)
    k1 = vector["K1Response"].to_numpy(float)
    k2 = vector["K2LockedA2Prediction"].to_numpy(float)
    sigma = np.sqrt(vector["CovarianceDiag"].to_numpy(float))

    poly_models = score[score["ModelID"].astype(str).str.startswith("POLY")]
    best_poly_id = str(poly_models.sort_values("AIC").iloc[0]["ModelID"])
    degree = int(best_poly_id.replace("POLY_DEG", ""))
    coeff = np.polyfit(vector["x_coordinate"].to_numpy(float), y, degree)
    best_poly = np.polyval(coeff, vector["x_coordinate"].to_numpy(float))

    audit = vector[
        [
            "GridIndex",
            "z_grid",
            "x_coordinate",
            "SourceSplitCandidate",
            "K1Response",
            "K2LockedA2Prediction",
            "CovarianceDiag",
        ]
    ].copy()
    audit["DepthZone"] = [depth_zone(x) for x in audit["x_coordinate"]]
    audit["SigmaDiag"] = sigma
    audit["BestPolyID"] = best_poly_id
    audit["BestPolyPrediction"] = best_poly
    audit["ResidualK1"] = y - k1
    audit["ResidualK2"] = y - k2
    audit["ResidualBestPoly"] = y - best_poly
    audit["K1Chi2DiagContribution"] = (audit["ResidualK1"] / sigma) ** 2
    audit["K2Chi2DiagContribution"] = (audit["ResidualK2"] / sigma) ** 2
    audit["BestPolyChi2DiagContribution"] = (audit["ResidualBestPoly"] / sigma) ** 2
    audit["DeltaChi2DiagK2MinusK1"] = audit["K2Chi2DiagContribution"] - audit["K1Chi2DiagContribution"]
    audit["DeltaChi2DiagK2MinusBestPoly"] = audit["K2Chi2DiagContribution"] - audit["BestPolyChi2DiagContribution"]
    audit["K2WorseThanK1"] = audit["DeltaChi2DiagK2MinusK1"] > 0
    audit["K2WorseThanBestPoly"] = audit["DeltaChi2DiagK2MinusBestPoly"] > 0
    audit["TargetSign"] = [signed_class(v) for v in y]
    audit["K1Sign"] = [signed_class(v) for v in k1]
    audit["K2Sign"] = [signed_class(v) for v in k2]
    audit["K2TargetSignMismatch"] = np.sign(y) != np.sign(k2)
    audit["K1TargetSignMismatch"] = np.sign(y) != np.sign(k1)

    reasons = []
    for _, row in audit.iterrows():
        row_reasons: list[str] = []
        if row["K2TargetSignMismatch"]:
            row_reasons.append("k2_target_sign_mismatch")
        if abs(row["K2LockedA2Prediction"]) > abs(row["SourceSplitCandidate"]) and row["K2WorseThanK1"]:
            row_reasons.append("locked_a2_overshoot_vs_candidate_target")
        if row["K2WorseThanBestPoly"]:
            row_reasons.append("flexible_polynomial_absorbs_candidate_shape")
        if row["K2WorseThanK1"] and not row_reasons:
            row_reasons.append("k1_closer_under_candidate_scale")
        if not row_reasons:
            row_reasons.append("k2_not_primary_row_driver")
        reasons.append(";".join(row_reasons))
    audit["WeakeningMechanism"] = reasons
    audit["MeasurementValidationAllowed"] = False
    audit["ClaimBoundary"] = "likelihood_native_rerun_weakening_diagnostic_no_measurement_validation"
    audit.to_csv(OUT_AUDIT, index=False)

    zone_rows = []
    for zone, group in audit.groupby("DepthZone", sort=False):
        zone_rows.append(
            {
                "SummaryID": f"ZONE_{zone.upper()}",
                "Rows": len(group),
                "DeltaChi2DiagK2MinusK1": float(group["DeltaChi2DiagK2MinusK1"].sum()),
                "DeltaChi2DiagK2MinusBestPoly": float(group["DeltaChi2DiagK2MinusBestPoly"].sum()),
                "K2WorseThanK1Rows": int(group["K2WorseThanK1"].sum()),
                "K2WorseThanBestPolyRows": int(group["K2WorseThanBestPoly"].sum()),
                "PrimaryMechanisms": ";".join(sorted(set(";".join(group["WeakeningMechanism"]).split(";")))),
            }
        )

    total_delta_k1 = float(audit["DeltaChi2DiagK2MinusK1"].sum())
    total_delta_poly = float(audit["DeltaChi2DiagK2MinusBestPoly"].sum())
    worst_k1 = audit.sort_values("DeltaChi2DiagK2MinusK1", ascending=False).iloc[0]
    worst_poly = audit.sort_values("DeltaChi2DiagK2MinusBestPoly", ascending=False).iloc[0]

    rows = [
        {
            "SummaryID": "LIKELIHOOD_NATIVE_RERUN_WEAKENING_OVERVIEW",
            "Rows": len(audit),
            "CandidateStatus": rerun["CurrentStatus"],
            "FullCovDeltaAIC_K2MinusK1": rerun["DeltaAIC_K2_minus_K1"],
            "FullCovDeltaAIC_K2MinusBestPoly": rerun["DeltaAIC_K2_minus_BestPoly"],
            "DiagDeltaChi2K2MinusK1": total_delta_k1,
            "DiagDeltaChi2K2MinusBestPoly": total_delta_poly,
            "K2WorseThanK1Rows": int(audit["K2WorseThanK1"].sum()),
            "K2WorseThanBestPolyRows": int(audit["K2WorseThanBestPoly"].sum()),
            "WorstK1GridIndex": int(worst_k1["GridIndex"]),
            "WorstK1Mechanism": worst_k1["WeakeningMechanism"],
            "WorstPolyGridIndex": int(worst_poly["GridIndex"]),
            "WorstPolyMechanism": worst_poly["WeakeningMechanism"],
            "MeasurementValidationAllowed": False,
            "CurrentStatus": "RERUN_WEAKENING_DIAGNOSED_NO_A2_CHANGE_AUTHORIZED",
            "StrongestAllowedClaim": "the locked public-covariance rerun is diagnosed as mixed/weakening without changing A2",
            "NextAction": "separate candidate-scale sign/overshoot rows from genuine covariance-native support before any stronger interpretation",
            "ClaimBoundary": "likelihood_native_rerun_weakening_diagnostic_no_measurement_validation",
        }
    ]
    rows.extend(zone_rows)
    pd.DataFrame(rows).to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
