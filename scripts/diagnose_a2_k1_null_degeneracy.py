#!/usr/bin/env python3
"""Diagnose local K1-null degeneracy for the A2 v3 candidate.

This audit asks whether a near-zero K1 row is a true no-signal row or a
cancellation/null of nonzero SN and BAO branch information. It does not change
the locked A2 prediction, does not refit K1, and does not use the target to
choose a sign.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"

K1 = DATA / "k1" / "source_split_external_k1_response.csv"
BASELINE = DATA / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
META = EVIDENCE / "source_split_coordinate_native_target.csv"
V3 = EVIDENCE / "a2_projection_gated_v3_candidate_prediction.csv"

OUT_AUDIT = EVIDENCE / "a2_k1_null_degeneracy_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_k1_null_degeneracy_summary.csv"

NULL_SIGMA_THRESHOLD = 0.05
NULL_ABS_THRESHOLD = 1.0e-3


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sign(value: float) -> int:
    if abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def safe_ratio(num: float, den: float) -> float:
    if abs(den) < 1e-12:
        return float("nan")
    return float(num / den)


def classify(row: pd.Series) -> tuple[str, str, str]:
    k1 = float(row["K1Response"])
    k1_sigma = float(row["K1Sigma"])
    target = float(row["SourceSplitCandidate"])
    centered = float(row["CenteredControlSourceSplitResponse"])
    sn = float(row["SNRawResidualMu"])
    bao = float(row["BAOBaselineLogResidual"])
    same_sign = truthy(row["SNBAOSameSign"])

    k1_z = abs(k1) / k1_sigma if k1_sigma > 0 else float("inf")
    branch_nonzero = max(abs(sn), abs(bao), abs(centered)) > 0.01
    target_large = abs(target) > 1.0
    cancellation = abs(k1) < max(NULL_ABS_THRESHOLD, NULL_SIGMA_THRESHOLD * k1_sigma) and branch_nonzero

    if cancellation and target_large and same_sign:
        return (
            "LOCAL_CANCELLATION_NULL_WITH_SOURCE_SUPPORT",
            "K1 raw source-split response is near zero because SN and BAO branches nearly cancel, not because the row is empty",
            "keep A2 suppressed until an independent source-branch sign/amplitude policy is frozen",
        )
    if cancellation and branch_nonzero:
        return (
            "LOCAL_CANCELLATION_NULL",
            "K1 is locally near zero while branch-level controls remain nonzero",
            "separate cancellation-null rows from no-signal rows in the next K1 export",
        )
    if k1_z < NULL_SIGMA_THRESHOLD:
        return (
            "STATISTICAL_K1_NULL",
            "K1 is statistically near zero under its exported sigma",
            "do not use multiplicative A2 to infer an independent sign",
        )
    return (
        "K1_NON_NULL_ROW",
        "K1 is not locally degenerate under the current thresholds",
        "keep current row class",
    )


def main() -> None:
    k1 = pd.read_csv(K1)
    baseline = pd.read_csv(BASELINE)
    vector = pd.read_csv(VECTOR)
    meta = pd.read_csv(META)
    v3 = pd.read_csv(V3)

    data = (
        vector.merge(
            k1[
                [
                    "GridIndex",
                    "K1Sigma",
                    "K1SourceID",
                    "ProvenanceType",
                    "AllowedAsPrimaryK1Candidate",
                    "ControlResponseColumn",
                    "ControlResponseValue",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(
            baseline[
                [
                    "GridIndex",
                    "SNRawResidualMu",
                    "SNSameSampleCenteredResidualMu",
                    "BAOBaselineLogResidual",
                    "RawSourceSplitResponse",
                    "CenteredControlSourceSplitResponse",
                    "JointSigmaDiagProxy",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(
            meta[["GridIndex", "SNStandardizedResidual", "BAOStandardizedResidual", "SNBAOSameSign", "SignStableTemplate"]],
            on="GridIndex",
            how="left",
        )
        .merge(
            v3[["GridIndex", "ProjectionState", "A2ProjectionGatedV3Prediction", "ProjectionMultiplier"]],
            on="GridIndex",
            how="left",
        )
        .sort_values("GridIndex")
    )

    rows = []
    for _, row in data.iterrows():
        class_id, interpretation, next_check = classify(row)
        k1_response = float(row["K1Response"])
        k1_sigma = float(row["K1Sigma"])
        target = float(row["SourceSplitCandidate"])
        centered = float(row["CenteredControlSourceSplitResponse"])
        raw = float(row["RawSourceSplitResponse"])
        sn = float(row["SNRawResidualMu"])
        bao = float(row["BAOBaselineLogResidual"])
        v3_pred = float(row["A2ProjectionGatedV3Prediction"])
        rows.append(
            {
                "AuditID": "A2_K1_NULL_DEGENERACY_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "ProjectionState": row["ProjectionState"],
                "NullClass": class_id,
                "SourceSplitCandidate": target,
                "K1Response": k1_response,
                "K1Sigma": k1_sigma,
                "K1AbsOverSigma": safe_ratio(abs(k1_response), k1_sigma),
                "K1NearZeroAbs": abs(k1_response) < NULL_ABS_THRESHOLD,
                "K1NearZeroSigma": safe_ratio(abs(k1_response), k1_sigma) < NULL_SIGMA_THRESHOLD,
                "SNRawResidualMu": sn,
                "BAOBaselineLogResidual": bao,
                "RawSourceSplitResponse": raw,
                "SNSameSampleCenteredResidualMu": row["SNSameSampleCenteredResidualMu"],
                "CenteredControlSourceSplitResponse": centered,
                "JointSigmaDiagProxy": row["JointSigmaDiagProxy"],
                "ControlResponseValue": row["ControlResponseValue"],
                "A2ProjectionGatedV3Prediction": v3_pred,
                "ProjectionMultiplier": row["ProjectionMultiplier"],
                "TargetSign": sign(target),
                "K1Sign": sign(k1_response),
                "CenteredControlSign": sign(centered),
                "SNRawSign": sign(sn),
                "BAORawSign": sign(bao),
                "SNBAOSameSign": row["SNBAOSameSign"],
                "SignStableTemplate": row["SignStableTemplate"],
                "TargetOverK1": safe_ratio(target, k1_response),
                "TargetOverCenteredControl": safe_ratio(target, centered),
                "CenteredControlOverK1": safe_ratio(centered, k1_response),
                "K1SourceID": row["K1SourceID"],
                "ProvenanceType": row["ProvenanceType"],
                "AllowedAsPrimaryK1Candidate": row["AllowedAsPrimaryK1Candidate"],
                "Interpretation": interpretation,
                "RequiredNextCheck": next_check,
                "AllowedToUnsuppressA2": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_k1_null_degeneracy_audit_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    null_rows = audit[~audit["NullClass"].eq("K1_NON_NULL_ROW")]
    cancellation_rows = audit[audit["NullClass"].astype(str).str.contains("CANCELLATION", na=False)]
    grid3 = audit[audit["GridIndex"].eq(3)].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "A2_K1_NULL_DEGENERACY_AUDIT_SUMMARY",
                "Rows": len(audit),
                "LocalNullRows": len(null_rows),
                "CancellationNullRows": len(cancellation_rows),
                "Grid3NullClass": grid3["NullClass"],
                "Grid3K1Response": grid3["K1Response"],
                "Grid3K1Sigma": grid3["K1Sigma"],
                "Grid3K1AbsOverSigma": grid3["K1AbsOverSigma"],
                "Grid3CenteredControl": grid3["CenteredControlSourceSplitResponse"],
                "Grid3TargetOverCenteredControl": grid3["TargetOverCenteredControl"],
                "Grid3TargetOverK1": grid3["TargetOverK1"],
                "Grid3AllowedToUnsuppressA2": False,
                "AllowedToUnsuppressA2": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "K1_NULL_IS_LOCAL_CANCELLATION_NOT_A2_ACTIVATION_PERMISSION",
                "StrongestAllowedClaim": "grid3 K1-null is a local cancellation-null with nonzero branch support",
                "RequiredNextCheck": "freeze an independent source-branch sign/amplitude policy before any A2 unsuppression rerun",
                "ClaimBoundary": "a2_k1_null_degeneracy_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
