#!/usr/bin/env python3
"""Audit the A2 cross-covariance policy against the source-branch warning.

This script records whether the registered SN-BAO cross-covariance policy is
usable for preflight interpretation of A2 without selecting rho_cross by score.
It does not tune rho_cross, does not change A2, and does not authorize
measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

CROSS_SUMMARY = EVIDENCE / "source_split_likelihood_native_cross_covariance_summary.csv"
POLICY = EVIDENCE / "k2_a2_cross_covariance_policy_v1.csv"
READINESS = EVIDENCE / "k2_a2_cross_covariance_policy_readiness_v1.csv"
SOURCE_NORM = EVIDENCE / "a2_source_branch_normalization_summary.csv"
JOINT = EVIDENCE / "source_split_joint_covariance_policy_summary.csv"

OUT_AUDIT = EVIDENCE / "a2_cross_covariance_policy_audit.csv"
OUT_SUMMARY = EVIDENCE / "a2_cross_covariance_policy_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    cross = pd.read_csv(CROSS_SUMMARY)
    policy = pd.read_csv(POLICY).iloc[0]
    readiness = pd.read_csv(READINESS).iloc[0]
    source_norm = pd.read_csv(SOURCE_NORM).iloc[0]
    joint = pd.read_csv(JOINT).iloc[0]

    pd_cross = cross[cross["BestModel"].notna()].copy()
    pd_cross["K2ImprovesOverK1Bool"] = pd_cross["K2ImprovesOverK1"].map(truthy)
    pd_cross["K2BeatsBestPolyBool"] = pd_cross["K2BeatsBestPoly"].map(truthy)

    zero = pd_cross[pd_cross["RhoCross"].astype(float).eq(0.0)].iloc[0]
    rows = []
    for _, row in pd_cross.iterrows():
        rows.append(
            {
                "AuditID": "A2_CROSS_COVARIANCE_POLICY_AUDIT_V1",
                "RhoCross": row["RhoCross"],
                "PositiveDefinite": True,
                "BestModel": row["BestModel"],
                "K1AIC": row["K1AIC"],
                "K2AIC": row["K2AIC"],
                "BestPolyAIC": row["BestPolyAIC"],
                "DeltaAIC_K2_minus_K1": row["DeltaAIC_K2_minus_K1"],
                "DeltaAIC_K2_minus_BestPoly": row["DeltaAIC_K2_minus_BestPoly"],
                "K2ImprovesOverK1": row["K2ImprovesOverK1"],
                "K2BeatsBestPoly": row["K2BeatsBestPoly"],
                "PolicySelectionAllowed": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "a2_cross_covariance_policy_audit_no_measurement_validation",
            }
        )
    pd.DataFrame(rows).to_csv(OUT_AUDIT, index=False)

    all_k2_gt_k1 = bool(pd_cross["K2ImprovesOverK1Bool"].all())
    any_k2_gt_poly = bool(pd_cross["K2BeatsBestPolyBool"].any())
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "A2_CROSS_COVARIANCE_POLICY_AUDIT_SUMMARY",
                "PolicyID": policy["PolicyID"],
                "PrimaryBenchmarkRule": policy["BenchmarkCrossCovarianceRule"],
                "RhoGridRows": len(cross),
                "PositiveDefiniteRhoRows": len(pd_cross),
                "RhoMinPD": float(pd_cross["RhoCross"].min()),
                "RhoMaxPD": float(pd_cross["RhoCross"].max()),
                "ZeroRhoK2ImprovesOverK1": zero["K2ImprovesOverK1"],
                "ZeroRhoK2BeatsBestPoly": zero["K2BeatsBestPoly"],
                "AllPDK2ImprovesOverK1": all_k2_gt_k1,
                "AnyPDK2BeatsBestPoly": any_k2_gt_poly,
                "PolicyFrozenForPreflight": readiness["PolicyFrozenForPreflight"],
                "TransformCovarianceReady": readiness["TransformCovarianceReady"],
                "JointPolicyPositiveDefinite": joint["PositiveDefinite"],
                "JointAllowedForK2Scoring": joint["AllowedForK2Scoring"],
                "SourceNormalizationStatus": source_norm["CurrentStatus"],
                "ActiveMeanPublicSigmaOverK1Sigma": source_norm["ActiveMeanPublicSigmaOverK1Sigma"],
                "ActiveMeanAbsTargetOverPublicSigma": source_norm["ActiveMeanAbsTargetOverPublicSigma"],
                "PolicySelectionAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "CROSS_COVARIANCE_PREFLIGHT_SUPPORTS_K2_OVER_K1_BUT_POLY_BLOCKS_MEASUREMENT"
                    if all_k2_gt_k1 and not any_k2_gt_poly
                    else "CROSS_COVARIANCE_PREFLIGHT_MIXED"
                ),
                "StrongestAllowedClaim": "registered cross-covariance policy supports A2 over K1 at preflight level but not over polynomial controls",
                "RequiredNextCheck": "replace zero-cross/preflight proxy with public/source-native joint covariance before stronger interpretation",
                "ClaimBoundary": "a2_cross_covariance_policy_audit_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
