#!/usr/bin/env python3
"""Diagnose source-branch and covariance normalization for A2 active rows.

This audit checks whether active-memory overshoot is tied to the response
normalization/covariance scale rather than a need to change A_tau. It does not
change A_tau, rho, p, K1, or any prediction.
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
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PUBLIC_MARGINALS = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
OVERSHOOT = EVIDENCE / "a2_active_memory_overshoot_audit.csv"
SCALE_SUMMARY = EVIDENCE / "source_split_likelihood_native_scale_covariance_summary.csv"

OUT_AUDIT = EVIDENCE / "a2_source_branch_normalization_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_source_branch_normalization_summary.csv"


def safe_ratio(num: float, den: float) -> float:
    if abs(den) < 1e-12:
        return float("nan")
    return float(num / den)


def classify(row: pd.Series) -> tuple[str, str, str]:
    public_to_k1_sigma = float(row["PublicSigmaOverK1Sigma"])
    target_over_public_sigma = abs(float(row["SourceSplitCandidate"])) / float(row["SigmaPublicProxy"])
    target_over_k1_sigma = abs(float(row["SourceSplitCandidate"])) / float(row["K1Sigma"])
    active = str(row["ProjectionState"]) == "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE"

    if active and public_to_k1_sigma > 10.0 and target_over_public_sigma < 1.0:
        return (
            "PUBLIC_COVARIANCE_RESCALES_ACTIVE_ROW",
            "public covariance proxy makes the active row a sub-sigma target while K1 sigma makes it look high tension",
            "prefer public/source-native covariance normalization before judging A_tau",
        )
    if active and target_over_k1_sigma > 5.0 and target_over_public_sigma < 2.0:
        return (
            "K1_SIGMA_UNDERSTATES_SOURCE_BRANCH_SCALE",
            "K1 sigma is too small relative to public branch covariance for active-memory amplitude interpretation",
            "do not refit A_tau; rerun with frozen public/source-native covariance",
        )
    if active:
        return (
            "ACTIVE_ROW_SCALE_REQUIRES_REVIEW",
            "active row is sensitive to normalization but not cleanly explained by public sigma ratio alone",
            "inspect transform and cross-covariance policy",
        )
    return (
        "NON_ACTIVE_REFERENCE_ROW",
        "row is not an active-memory overshoot row",
        "retain as reference",
    )


def main() -> None:
    k1 = pd.read_csv(K1)
    baseline = pd.read_csv(BASELINE)
    target = pd.read_csv(TARGET)
    public = pd.read_csv(PUBLIC_MARGINALS)
    overshoot = pd.read_csv(OVERSHOOT)
    scale = pd.read_csv(SCALE_SUMMARY)

    data = (
        k1[["GridIndex", "z_grid", "x_coordinate", "K1Response", "K1Sigma"]]
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
            target[
                [
                    "GridIndex",
                    "SourceSplitResponse",
                    "SNStandardizedResidual",
                    "BAOStandardizedResidual",
                    "SNBAOSameSign",
                    "SignStableTemplate",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(public[["GridIndex", "SigmaPublicProxy"]], on="GridIndex", how="left")
        .merge(
            overshoot[
                [
                    "GridIndex",
                    "A2ProjectionGatedV3Prediction",
                    "LockedProjectionMultiplier",
                    "TargetImpliedATau",
                    "OvershootClass",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .sort_values("GridIndex")
    )
    data["ProjectionState"] = np.where(
        data["OvershootClass"].notna(),
        "SOURCE_ANTI_COHERENT_MEMORY_ACTIVE",
        "NON_ACTIVE",
    )

    rows = []
    for _, row in data.iterrows():
        source_target = float(row["SourceSplitResponse"])
        k1_sigma = float(row["K1Sigma"])
        public_sigma = float(row["SigmaPublicProxy"])
        centered = float(row["CenteredControlSourceSplitResponse"])
        row = row.copy()
        row["SourceSplitCandidate"] = source_target
        row["PublicSigmaOverK1Sigma"] = safe_ratio(public_sigma, k1_sigma)
        class_id, interpretation, next_check = classify(row)
        rows.append(
            {
                "AuditID": "A2_SOURCE_BRANCH_NORMALIZATION_AUDIT_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": row["z_grid"],
                "x_coordinate": row["x_coordinate"],
                "ProjectionState": row["ProjectionState"],
                "NormalizationClass": class_id,
                "SourceSplitCandidate": source_target,
                "K1Response": row["K1Response"],
                "A2ProjectionGatedV3Prediction": row["A2ProjectionGatedV3Prediction"],
                "K1Sigma": k1_sigma,
                "SigmaPublicProxy": public_sigma,
                "JointSigmaDiagProxy": row["JointSigmaDiagProxy"],
                "PublicSigmaOverK1Sigma": safe_ratio(public_sigma, k1_sigma),
                "PublicSigmaOverJointSigma": safe_ratio(public_sigma, float(row["JointSigmaDiagProxy"])),
                "AbsTargetOverK1Sigma": safe_ratio(abs(source_target), k1_sigma),
                "AbsTargetOverPublicSigma": safe_ratio(abs(source_target), public_sigma),
                "AbsTargetOverJointSigma": safe_ratio(abs(source_target), float(row["JointSigmaDiagProxy"])),
                "SNRawResidualMu": row["SNRawResidualMu"],
                "BAOBaselineLogResidual": row["BAOBaselineLogResidual"],
                "RawSourceSplitResponse": row["RawSourceSplitResponse"],
                "CenteredControlSourceSplitResponse": centered,
                "AbsCenteredControlOverK1Sigma": safe_ratio(abs(centered), k1_sigma),
                "AbsCenteredControlOverPublicSigma": safe_ratio(abs(centered), public_sigma),
                "SNStandardizedResidual": row["SNStandardizedResidual"],
                "BAOStandardizedResidual": row["BAOStandardizedResidual"],
                "SNBAOSameSign": row["SNBAOSameSign"],
                "SignStableTemplate": row["SignStableTemplate"],
                "LockedProjectionMultiplier": row["LockedProjectionMultiplier"],
                "TargetImpliedATau": row["TargetImpliedATau"],
                "OvershootClass": row["OvershootClass"],
                "Interpretation": interpretation,
                "RequiredNextCheck": next_check,
                "AllowedToChangeATau": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_source_branch_normalization_audit_no_measurement_validation",
            }
        )
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    active = audit[audit["ProjectionState"].eq("SOURCE_ANTI_COHERENT_MEMORY_ACTIVE")]
    scale_case = scale[scale["CovarianceCase"].eq("diag_target_fraction_floor_25pct")].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "A2_SOURCE_BRANCH_NORMALIZATION_AUDIT_SUMMARY",
                "Rows": len(audit),
                "ActiveMemoryRows": len(active),
                "ActiveRowsRescaledByPublicCovariance": int(
                    active["NormalizationClass"].eq("PUBLIC_COVARIANCE_RESCALES_ACTIVE_ROW").sum()
                ),
                "ActiveMeanPublicSigmaOverK1Sigma": float(active["PublicSigmaOverK1Sigma"].mean())
                if len(active)
                else float("nan"),
                "ActiveMeanAbsTargetOverK1Sigma": float(active["AbsTargetOverK1Sigma"].mean())
                if len(active)
                else float("nan"),
                "ActiveMeanAbsTargetOverPublicSigma": float(active["AbsTargetOverPublicSigma"].mean())
                if len(active)
                else float("nan"),
                "TargetFraction25pctK2ImprovesOverK1": scale_case["K2ImprovesOverK1"],
                "TargetFraction25pctK2BeatsBestPoly": scale_case["K2BeatsBestPoly"],
                "AllowedToChangeATau": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "ACTIVE_OVERSHOOT_EXPLAINED_BY_SOURCE_BRANCH_NORMALIZATION_WARNING",
                "StrongestAllowedClaim": "active-memory overshoot is consistent with source-branch covariance normalization mismatch",
                "RequiredNextCheck": "promote public/source-native covariance and cross-covariance policy before rerunning locked A2",
                "ClaimBoundary": "a2_source_branch_normalization_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
