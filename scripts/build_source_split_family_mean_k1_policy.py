#!/usr/bin/env python3
"""Build source-split family-mean K1 policy readiness table."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
FAMILIES = ROOT / "data" / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
POLICY_OUT = EVIDENCE / "source_split_family_mean_k1_policy.csv"
READINESS_OUT = EVIDENCE / "source_split_family_mean_k1_policy_readiness.csv"


def candidate_stats() -> dict[str, object]:
    if not FAMILIES.exists():
        return {
            "FamilyExportAvailable": False,
            "FamilyCount": 0,
            "UsableRows": 0,
            "EqualWeightNonzeroRows": 0,
            "MeanAbsEqualWeightResponse": np.nan,
        }
    families = pd.read_csv(FAMILIES)
    target = pd.read_csv(TARGET)
    usable_indices = (
        target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]["GridIndex"]
        .astype(int)
        .tolist()
    )
    pivot = families[families["GridIndex"].astype(int).isin(usable_indices)].pivot_table(
        index="GridIndex",
        columns="FamilyID",
        values="ResponseValue",
        aggfunc="first",
    )
    equal_weight = pivot.mean(axis=1)
    return {
        "FamilyExportAvailable": True,
        "FamilyCount": int(families["FamilyID"].nunique()),
        "UsableRows": len(usable_indices),
        "EqualWeightNonzeroRows": int((~np.isclose(equal_weight.to_numpy(float), 0.0)).sum()),
        "MeanAbsEqualWeightResponse": float(np.mean(np.abs(equal_weight.to_numpy(float)))),
    }


def policy_rows(stats: dict[str, object]) -> list[dict[str, object]]:
    return [
        {
            "PolicyID": "FMK1_EQUAL_WEIGHT_SIGNED_MEAN_V1",
            "PolicyClass": "external_reconstruction_family_mean",
            "Definition": "K1Response = arithmetic mean of signed reconstruction-family responses on each source-split row",
            "RequiresFamilyCountAtLeast": 2,
            "RequiresPublicSN": True,
            "RequiresPublicBAO": True,
            "RequiresJointCovariance": True,
            "RequiresPredeclaredBeforeK2Scoring": True,
            "FrozenBeforeCurrentScorecard": False,
            "UsesSameDataAmplitudeFit": False,
            "AllowsSingleBranchSubstitution": False,
            "CurrentFamilyCount": stats["FamilyCount"],
            "CurrentNonzeroRows": stats["EqualWeightNonzeroRows"],
            "CurrentMeanAbsResponse": stats["MeanAbsEqualWeightResponse"],
            "AllowedForCurrentExternalK1Export": False,
            "BlockingIssue": "policy_declared_after_current_k2_scorecard;independence_policy_not_declared_before_sensitivity",
            "NextAction": "Freeze this policy only for a future rerun, or replace it with a likelihood-native K1 baseline.",
            "ClaimBoundary": "family_mean_policy_only_no_measurement_validation",
        },
        {
            "PolicyID": "FMK1_INVERSE_VARIANCE_MEAN_V1",
            "PolicyClass": "external_reconstruction_family_mean",
            "Definition": "K1Response = inverse-variance weighted mean of reconstruction-family responses",
            "RequiresFamilyCountAtLeast": 2,
            "RequiresPublicSN": True,
            "RequiresPublicBAO": True,
            "RequiresJointCovariance": True,
            "RequiresPredeclaredBeforeK2Scoring": True,
            "FrozenBeforeCurrentScorecard": False,
            "UsesSameDataAmplitudeFit": False,
            "AllowsSingleBranchSubstitution": False,
            "CurrentFamilyCount": stats["FamilyCount"],
            "CurrentNonzeroRows": "",
            "CurrentMeanAbsResponse": "",
            "AllowedForCurrentExternalK1Export": False,
            "BlockingIssue": "family_covariance_weights_not_declared;policy_declared_after_current_k2_scorecard",
            "NextAction": "Declare family covariance weights before any future K2 scoring rerun.",
            "ClaimBoundary": "family_mean_policy_only_no_measurement_validation",
        },
        {
            "PolicyID": "FMK1_ROBUST_MEDIAN_FAMILY_RESPONSE_V1",
            "PolicyClass": "external_reconstruction_family_mean",
            "Definition": "K1Response = robust median across at least three reconstruction-family responses",
            "RequiresFamilyCountAtLeast": 3,
            "RequiresPublicSN": True,
            "RequiresPublicBAO": True,
            "RequiresJointCovariance": True,
            "RequiresPredeclaredBeforeK2Scoring": True,
            "FrozenBeforeCurrentScorecard": False,
            "UsesSameDataAmplitudeFit": False,
            "AllowsSingleBranchSubstitution": False,
            "CurrentFamilyCount": stats["FamilyCount"],
            "CurrentNonzeroRows": "",
            "CurrentMeanAbsResponse": "",
            "AllowedForCurrentExternalK1Export": False,
            "BlockingIssue": "requires_at_least_three_reconstruction_families;policy_declared_after_current_k2_scorecard",
            "NextAction": "Add an independent third reconstruction family before using a robust median K1.",
            "ClaimBoundary": "family_mean_policy_only_no_measurement_validation",
        },
        {
            "PolicyID": "FMK1_SIGN_STABLE_ROWS_ONLY_V1",
            "PolicyClass": "diagnostic_control",
            "Definition": "K1Response defined only on rows where all reconstruction-family signs agree",
            "RequiresFamilyCountAtLeast": 2,
            "RequiresPublicSN": True,
            "RequiresPublicBAO": True,
            "RequiresJointCovariance": True,
            "RequiresPredeclaredBeforeK2Scoring": True,
            "FrozenBeforeCurrentScorecard": False,
            "UsesSameDataAmplitudeFit": False,
            "AllowsSingleBranchSubstitution": False,
            "CurrentFamilyCount": stats["FamilyCount"],
            "CurrentNonzeroRows": "",
            "CurrentMeanAbsResponse": "",
            "AllowedForCurrentExternalK1Export": False,
            "BlockingIssue": "does_not_cover_all_usable_rows;diagnostic_control_not_primary_k1",
            "NextAction": "Keep as subset diagnostic only, not primary source-split K1.",
            "ClaimBoundary": "family_mean_policy_only_no_measurement_validation",
        },
    ]


def readiness(policy: pd.DataFrame, stats: dict[str, object]) -> pd.DataFrame:
    allowed = policy[policy["AllowedForCurrentExternalK1Export"].astype(bool)]
    return pd.DataFrame(
        [
            {
                "GateID": "SOURCE_SPLIT_FAMILY_MEAN_K1_POLICY_V1",
                "FamilyExportAvailable": stats["FamilyExportAvailable"],
                "FamilyCount": stats["FamilyCount"],
                "UsableRows": stats["UsableRows"],
                "PolicyCount": len(policy),
                "AllowedPolicyCount": len(allowed),
                "EqualWeightNonzeroRows": stats["EqualWeightNonzeroRows"],
                "MeanAbsEqualWeightResponse": stats["MeanAbsEqualWeightResponse"],
                "CurrentExternalK1ExportAllowed": len(allowed) > 0,
                "BlockingIssue": "no_family_mean_policy_was_frozen_before_current_k2_scorecard",
                "NextAction": "Select and freeze a family-mean policy for a future rerun, or use a likelihood-native joint baseline.",
                "ClaimBoundary": "family_mean_policy_only_no_measurement_validation",
            }
        ]
    )


def main() -> None:
    stats = candidate_stats()
    policy = pd.DataFrame(policy_rows(stats))
    policy.to_csv(POLICY_OUT, index=False)
    readiness(policy, stats).to_csv(READINESS_OUT, index=False)
    print(f"Wrote {POLICY_OUT}")
    print(f"Wrote {READINESS_OUT}")


if __name__ == "__main__":
    main()
