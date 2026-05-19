#!/usr/bin/env python3
"""Diagnose which structural mechanisms dominate the remaining A2 v3 residuals.

This is an audit only. It does not change the locked K2 kernel, does not refit
K1, and does not use the target sign to create a new prediction.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
PRED = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"

OUT_AUDIT = EVIDENCE / "a2_v3_residual_mechanism_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_v3_residual_mechanism_summary.csv"


def load_covariance(path: Path, grid: list[int]) -> np.ndarray:
    rows = pd.read_csv(path).set_index("GridIndex").loc[grid]
    return rows[[str(idx) for idx in grid]].to_numpy(float)


def sign(value: float) -> int:
    if abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def classify(row: pd.Series) -> tuple[str, str, str]:
    state = str(row["ProjectionState"])
    target = float(row["SourceSplitCandidate"])
    k1 = float(row["K1Response"])
    v3 = float(row["A2ProjectionGatedV3Prediction"])
    multiplier = float(row["ProjectionMultiplier"])
    abs_target = abs(target)
    abs_k1 = abs(k1)
    abs_v3 = abs(v3)

    if state == "SOURCE_COHERENT_COMMON_MODE":
        if sign(target) != sign(k1) and abs_target > 1.0:
            return (
                "COMMON_MODE_BASELINE_MISALIGNMENT",
                "same-direction source branch is not safely removable as a pure common mode",
                "requires coordinate/native common-mode baseline audit before A2 can decide this row",
            )
        return (
            "COMMON_MODE_LOW_INFORMATION",
            "same-direction source branch is treated as baseline-like by the current structural rule",
            "keep conservative unless an independent common-mode baseline is exported",
        )

    if state == "K1_NULL_SUPPRESSED":
        if abs_k1 < 0.001 and abs_target > 1.0:
            return (
                "K1_NULL_DEGENERACY",
                "the frozen K1 baseline is nearly zero while the diagnostic target is large",
                "do not invent sign from A2; require independent K1/source-branch export",
            )
        return (
            "K1_NULL_LOW_INFORMATION",
            "near-null baseline limits memory activation without a sign source",
            "keep suppressed unless a non-target sign source is registered",
        )

    if state == "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE":
        if abs_v3 > abs_target * 2.0 and multiplier > 1.0:
            return (
                "ACTIVE_MEMORY_OVERSHOOT",
                "anti-coherent source-split row activates A2 but the locked amplitude is too large for the target size",
                "test whether covariance/source-branch normalization, not A_tau refit, explains the scale",
            )
        return (
            "ACTIVE_MEMORY_USEFUL",
            "anti-coherent source-split row is the intended A2 memory-active channel",
            "retain as the primary Tau Core structural support zone",
        )

    if state == "SIGN_UNSTABLE_UNIT_MEMORY":
        return (
            "SIGN_UNSTABLE_PARTIAL_RECOVERY",
            "sign-unstable rows improve when given unit memory without A_tau amplification",
            "treat as supportive for bounded memory, not as A_tau=2 measurement",
        )

    if state == "LOW_DEPTH_BASELINE":
        return (
            "LOW_DEPTH_WEAK_RESPONSE",
            "low-depth rows are expected to carry weak finite-memory response",
            "retain as a sanity check against early-depth overactivation",
        )

    return (
        "UNCLASSIFIED",
        "projection state has no registered mechanism interpretation",
        "inspect row manually",
    )


def main() -> None:
    vector = pd.read_csv(VECTOR)
    pred = pd.read_csv(PRED)
    data = vector.merge(
        pred[
            [
                "GridIndex",
                "ProjectionState",
                "ProjectionMultiplier",
                "K1Response",
                "A2ScalarV1Prediction",
                "A2ProjectionGatedV2Prediction",
                "A2ProjectionGatedV3Prediction",
                "SignStableTemplate",
                "SNBAOSameSign",
                "RuleReason",
            ]
        ],
        on=["GridIndex", "K1Response"],
        how="inner",
    ).sort_values("GridIndex")
    grid = data["GridIndex"].astype(int).to_list()
    sigma = np.sqrt(np.diag(load_covariance(COV, grid)))

    rows = []
    for i, row in data.reset_index(drop=True).iterrows():
        target = float(row["SourceSplitCandidate"])
        k1 = float(row["K1Response"])
        v1 = float(row["A2ScalarV1Prediction"])
        v2 = float(row["A2ProjectionGatedV2Prediction"])
        v3 = float(row["A2ProjectionGatedV3Prediction"])
        sigma_i = float(sigma[i])
        mechanism, interpretation, next_check = classify(row)
        k1_chi = ((target - k1) / sigma_i) ** 2
        v1_chi = ((target - v1) / sigma_i) ** 2
        v2_chi = ((target - v2) / sigma_i) ** 2
        v3_chi = ((target - v3) / sigma_i) ** 2
        rows.append(
            {
                "AuditID": "A2_V3_RESIDUAL_MECHANISM_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "ProjectionState": row["ProjectionState"],
                "MechanismClass": mechanism,
                "SourceSplitCandidate": target,
                "K1Response": k1,
                "A2ScalarV1Prediction": v1,
                "A2ProjectionGatedV2Prediction": v2,
                "A2ProjectionGatedV3Prediction": v3,
                "ProjectionMultiplier": row["ProjectionMultiplier"],
                "SigmaDiag": sigma_i,
                "K1Residual": target - k1,
                "V3Residual": target - v3,
                "K1Chi2Contribution": k1_chi,
                "V1Chi2Contribution": v1_chi,
                "V2Chi2Contribution": v2_chi,
                "V3Chi2Contribution": v3_chi,
                "DeltaChi2_V3_minus_K1": v3_chi - k1_chi,
                "DeltaChi2_V3_minus_V2": v3_chi - v2_chi,
                "V3ImprovesOverK1Row": v3_chi < k1_chi,
                "V3ImprovesOverV2Row": v3_chi < v2_chi,
                "TargetSign": sign(target),
                "K1Sign": sign(k1),
                "V3Sign": sign(v3),
                "SignStableTemplate": row["SignStableTemplate"],
                "SNBAOSameSign": row["SNBAOSameSign"],
                "MechanismInterpretation": interpretation,
                "RequiredNextCheck": next_check,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_residual_mechanism_audit_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(rows)
    audit["V3ContributionRank"] = audit["V3Chi2Contribution"].rank(ascending=False, method="first").astype(int)
    audit["K1AdvantageRank"] = audit["DeltaChi2_V3_minus_K1"].rank(ascending=False, method="first").astype(int)
    audit.to_csv(OUT_AUDIT, index=False)

    by_mechanism = (
        audit.groupby("MechanismClass", dropna=False)
        .agg(
            Rows=("GridIndex", "count"),
            V3ImprovesOverK1Rows=("V3ImprovesOverK1Row", "sum"),
            V3ImprovesOverV2Rows=("V3ImprovesOverV2Row", "sum"),
            SumK1Chi2=("K1Chi2Contribution", "sum"),
            SumV3Chi2=("V3Chi2Contribution", "sum"),
            MeanDeltaChi2V3MinusK1=("DeltaChi2_V3_minus_K1", "mean"),
            MaxV3ContributionRank=("V3ContributionRank", "min"),
        )
        .reset_index()
    )
    by_mechanism["DeltaChi2V3MinusK1"] = by_mechanism["SumV3Chi2"] - by_mechanism["SumK1Chi2"]
    by_mechanism["SummaryID"] = "A2_V3_RESIDUAL_MECHANISM_BY_CLASS"
    by_mechanism["MeasurementValidationAllowed"] = False
    by_mechanism["ClaimBoundary"] = "a2_v3_residual_mechanism_audit_no_measurement_validation"

    worst = audit.sort_values("V3Chi2Contribution", ascending=False).head(4)
    worst_rows = []
    for _, row in worst.iterrows():
        worst_rows.append(
            {
                "SummaryID": "A2_V3_RESIDUAL_MECHANISM_WORST_ROWS",
                "MechanismClass": row["MechanismClass"],
                "Rows": 1,
                "V3ImprovesOverK1Rows": int(row["V3ImprovesOverK1Row"]),
                "V3ImprovesOverV2Rows": int(row["V3ImprovesOverV2Row"]),
                "SumK1Chi2": row["K1Chi2Contribution"],
                "SumV3Chi2": row["V3Chi2Contribution"],
                "MeanDeltaChi2V3MinusK1": row["DeltaChi2_V3_minus_K1"],
                "MaxV3ContributionRank": row["V3ContributionRank"],
                "DeltaChi2V3MinusK1": row["DeltaChi2_V3_minus_K1"],
                "WorstGridIndex": row["GridIndex"],
                "RequiredNextCheck": row["RequiredNextCheck"],
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_residual_mechanism_audit_no_measurement_validation",
            }
        )

    total_delta = float(audit["DeltaChi2_V3_minus_K1"].sum())
    overview = pd.DataFrame(
        [
            {
                "SummaryID": "A2_V3_RESIDUAL_MECHANISM_OVERVIEW",
                "MechanismClass": "ALL_ROWS",
                "Rows": len(audit),
                "V3ImprovesOverK1Rows": int(audit["V3ImprovesOverK1Row"].sum()),
                "V3ImprovesOverV2Rows": int(audit["V3ImprovesOverV2Row"].sum()),
                "SumK1Chi2": float(audit["K1Chi2Contribution"].sum()),
                "SumV3Chi2": float(audit["V3Chi2Contribution"].sum()),
                "MeanDeltaChi2V3MinusK1": float(audit["DeltaChi2_V3_minus_K1"].mean()),
                "MaxV3ContributionRank": 1,
                "DeltaChi2V3MinusK1": total_delta,
                "CurrentStatus": (
                    "A2_V3_WEAKLY_SUPPORTIVE_WITH_STRUCTURAL_RESIDUALS"
                    if total_delta < 0
                    else "A2_V3_NOT_SUPPORTIVE_AGAINST_K1"
                ),
                "PrimaryResidualMechanisms": "common_mode_baseline_misalignment;k1_null_degeneracy;active_memory_overshoot",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_v3_residual_mechanism_audit_no_measurement_validation",
            }
        ]
    )

    summary = pd.concat([overview, by_mechanism, pd.DataFrame(worst_rows)], ignore_index=True, sort=False)
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
