#!/usr/bin/env python3
"""Build preregistered future rerun protocol for source-split K2 tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
PROTOCOL_OUT = EVIDENCE / "source_split_future_rerun_protocol.csv"
SUMMARY_OUT = EVIDENCE / "source_split_future_rerun_protocol_summary.csv"


def protocol_rows() -> list[dict[str, object]]:
    return [
        {
            "ProtocolID": "SSRERUN_LIKELIHOOD_NATIVE_K1_V1",
            "ProtocolClass": "preferred_future_rerun",
            "K1SourceRoute": "K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE",
            "K1PolicyID": "LIKELIHOOD_NATIVE_FROZEN_BASELINE",
            "K1ExportRequired": "data/k1/source_split_external_k1_response.csv",
            "K1FrozenBeforeRerun": True,
            "K1CanUseCurrentK2Residuals": False,
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2KernelChangeAllowed": False,
            "RhoUpperBound": 4.0,
            "AllowsRhoAboveBound": False,
            "CovarianceRequirement": "public_full_or_declared_shrinkage_joint_covariance",
            "NullComparatorsRequired": "K1_NO_MEMORY;POLY_DEG2;POLY_DEG3;BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "SignRuleRequirement": "predeclared_family_sign_stability_rule_with_warning_rows_retained",
            "CoordinateRequirement": "coordinate_native_or_likelihood_native_x_mapping_frozen_before_rerun",
            "CurrentStatus": "planned",
            "AllowedForCurrentRerun": False,
            "BlockingIssue": "likelihood_native_k1_export_missing",
            "SuccessCondition": "locked K2 competitive with null comparators under the same covariance without rho>4 or kernel changes",
            "WeakeningCondition": "K1/no-memory or simpler null remains preferred under the same covariance",
            "StrongNegativeCondition": "sign-stable rows contradict locked K2 or comparison requires rho>4/kernel change",
            "ClaimBoundary": "future_rerun_protocol_only_no_measurement_validation",
        },
        {
            "ProtocolID": "SSRERUN_FAMILY_MEAN_EQUAL_WEIGHT_V1",
            "ProtocolClass": "secondary_future_preflight",
            "K1SourceRoute": "K1SRC_EXTERNAL_RECONSTRUCTION_FAMILY_MEAN",
            "K1PolicyID": "FMK1_EQUAL_WEIGHT_SIGNED_MEAN_V1",
            "K1ExportRequired": "data/k1/source_split_external_k1_response.csv",
            "K1FrozenBeforeRerun": True,
            "K1CanUseCurrentK2Residuals": False,
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2KernelChangeAllowed": False,
            "RhoUpperBound": 4.0,
            "AllowsRhoAboveBound": False,
            "CovarianceRequirement": "declared_joint_source_split_covariance",
            "NullComparatorsRequired": "K1_NO_MEMORY;POLY_DEG2;POLY_DEG3;SIGN_RANDOMIZED_CONTROL",
            "SignRuleRequirement": "predeclared_family_sign_stability_rule_with_warning_rows_retained",
            "CoordinateRequirement": "x_chi_normalized_flat_lcdm_audit_or_declared_likelihood_native_mapping",
            "CurrentStatus": "candidate_policy_not_frozen_before_current_scorecard",
            "AllowedForCurrentRerun": False,
            "BlockingIssue": "policy_declared_after_current_k2_scorecard;external_k1_export_missing",
            "SuccessCondition": "future rerun only: family-mean K1 must be frozen before scoring and K2 must outperform/null-match controls without post-hoc changes",
            "WeakeningCondition": "family-mean K1 performs no better than no-memory or worsens K2 under shared covariance",
            "StrongNegativeCondition": "requires same-data amplitude rescue, single-branch substitution, rho>4, or kernel change",
            "ClaimBoundary": "future_rerun_protocol_only_no_measurement_validation",
        },
        {
            "ProtocolID": "SSRERUN_FORBIDDEN_CURRENT_SCORECARD_RESCUE",
            "ProtocolClass": "forbidden_path",
            "K1SourceRoute": "K1SRC_SAME_DATA_AMPLITUDE_RESCUE",
            "K1PolicyID": "POST_HOC_SCORECARD_K1",
            "K1ExportRequired": "",
            "K1FrozenBeforeRerun": False,
            "K1CanUseCurrentK2Residuals": True,
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2KernelChangeAllowed": False,
            "RhoUpperBound": 4.0,
            "AllowsRhoAboveBound": False,
            "CovarianceRequirement": "not_allowed",
            "NullComparatorsRequired": "not_allowed",
            "SignRuleRequirement": "not_allowed",
            "CoordinateRequirement": "not_allowed",
            "CurrentStatus": "forbidden",
            "AllowedForCurrentRerun": False,
            "BlockingIssue": "post_hoc_k1_rescue;uses_current_k2_residuals",
            "SuccessCondition": "none",
            "WeakeningCondition": "not_applicable",
            "StrongNegativeCondition": "any use of this path invalidates measurement-gate interpretation",
            "ClaimBoundary": "future_rerun_protocol_only_no_measurement_validation",
        },
    ]


def summary(protocol: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "GateID": "SOURCE_SPLIT_FUTURE_RERUN_PROTOCOL_V1",
                "ProtocolCount": len(protocol),
                "AllowedCurrentRerunCount": int(protocol["AllowedForCurrentRerun"].astype(bool).sum()),
                "PreferredProtocol": "SSRERUN_LIKELIHOOD_NATIVE_K1_V1",
                "SecondaryProtocol": "SSRERUN_FAMILY_MEAN_EQUAL_WEIGHT_V1",
                "ForbiddenProtocol": "SSRERUN_FORBIDDEN_CURRENT_SCORECARD_RESCUE",
                "K2KernelChangeAllowed": False,
                "RhoUpperBound": 4.0,
                "CurrentDecision": "no_current_rerun_authorized",
                "NextAction": "Create a predeclared external K1 export before running any new source-split K2/null scorecard.",
                "ClaimBoundary": "future_rerun_protocol_only_no_measurement_validation",
            }
        ]
    )


def main() -> None:
    protocol = pd.DataFrame(protocol_rows())
    protocol.to_csv(PROTOCOL_OUT, index=False)
    summary(protocol).to_csv(SUMMARY_OUT, index=False)
    print(f"Wrote {PROTOCOL_OUT}")
    print(f"Wrote {SUMMARY_OUT}")


if __name__ == "__main__":
    main()
