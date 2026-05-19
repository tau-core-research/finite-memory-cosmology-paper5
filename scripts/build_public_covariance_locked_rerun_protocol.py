#!/usr/bin/env python3
"""Build a locked protocol for the next public-covariance K2 rerun.

This protocol is a preregistration artifact. It does not run a new scorecard
and it does not authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

UPGRADE_READINESS = ROOT / "evidence" / "public_covariance_upgrade_readiness.csv"
OUT_PROTOCOL = ROOT / "evidence" / "public_covariance_locked_rerun_protocol.csv"
OUT_READINESS = ROOT / "evidence" / "public_covariance_locked_rerun_readiness.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    upgrade = pd.read_csv(UPGRADE_READINESS).iloc[0]

    protocol_rows = [
        {
            "ProtocolID": "PCOV_RERUN_FULL_LIKELIHOOD_NATIVE_V1",
            "RouteClass": "preferred_public_benchmark",
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2Kernel": "W(x)=1+rho*x^3",
            "P": 3,
            "RhoMax": 4.0,
            "RhoGreaterThan4Allowed": False,
            "K1SourceRequirement": "likelihood_native_joint_SN_BAO_no_memory_baseline_frozen_before_run",
            "CovarianceRequirement": "public_full_or_registered_shrinkage_SN_BAO_covariance_in_source_split_space",
            "CrossCovariancePolicyRequirement": "SN_BAO_cross_covariance_policy_declared_before_run",
            "CoordinateRequirement": "likelihood_native_or_declared_coordinate_native_mapping_frozen_before_run",
            "NullComparators": "K1_NO_MEMORY;POLY_DEG2;POLY_DEG3;ZERO_RESPONSE_CONTROL;SIGN_RANDOMIZED_CONTROL;COORDINATE_REMAP_CONTROL",
            "ValidationModes": "in_sample_AIC_BIC;leave_one_out;blocked_split;sign_stable_subset",
            "SuccessCondition": "K2 improves over K1 and is competitive with polynomial controls under the same registered covariance and validation policy",
            "WeakeningCondition": "K2 improves over K1 but polynomial controls dominate under public covariance",
            "StrongNegativeCondition": "K2 requires rho>4, kernel change, post_hoc_K1, or loses to K1 under registered public covariance",
            "CurrentAllowedToRun": False,
            "BlockingIssue": "full_public_covariance_transform_or_registered_shrinkage_route_missing",
            "ClaimBoundary": "locked_rerun_protocol_no_measurement_validation",
        },
        {
            "ProtocolID": "PCOV_RERUN_BRANCH_SCATTER_REGISTERED_V1",
            "RouteClass": "secondary_preflight_bridge",
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2Kernel": "W(x)=1+rho*x^3",
            "P": 3,
            "RhoMax": 4.0,
            "RhoGreaterThan4Allowed": False,
            "K1SourceRequirement": "current_likelihood_native_K1_or_registered_successor_frozen_before_run",
            "CovarianceRequirement": "branch_scatter_registered_as_systematic_or_reconstruction_family_scatter_before_run",
            "CrossCovariancePolicyRequirement": "not_applicable_unless_combined_with_public_covariance",
            "CoordinateRequirement": "current_CMB_chi_coordinate_or_declared_successor_frozen_before_run",
            "NullComparators": "K1_NO_MEMORY;POLY_DEG2;POLY_DEG3;ZERO_RESPONSE_CONTROL",
            "ValidationModes": "in_sample_AIC_BIC;leave_one_out;blocked_split",
            "SuccessCondition": "K2 remains best or competitive under registered branch-scatter covariance without post_hoc route changes",
            "WeakeningCondition": "K2 remains better than K1 but loses to polynomial controls under registered branch-scatter covariance",
            "StrongNegativeCondition": "branch_scatter cannot be independently classified beyond sensitivity route",
            "CurrentAllowedToRun": False,
            "BlockingIssue": "branch_scatter_route_not_classified_as_independent_systematic_or_scatter_source",
            "ClaimBoundary": "locked_rerun_protocol_no_measurement_validation",
        },
        {
            "ProtocolID": "PCOV_RERUN_FORBIDDEN_RESCUE_ROUTE",
            "RouteClass": "forbidden",
            "K2OperatorFile": "frozen/k2_operator_v1.yaml",
            "K2Kernel": "W(x)=1+rho*x^3",
            "P": 3,
            "RhoMax": 4.0,
            "RhoGreaterThan4Allowed": False,
            "K1SourceRequirement": "forbidden_if_derived_from_current_K2_residuals_or_scorecard_failure",
            "CovarianceRequirement": "forbidden_if_selected_after_seeing_K2_vs_polynomial_result",
            "CrossCovariancePolicyRequirement": "forbidden_if_tuned_to_make_K2_win",
            "CoordinateRequirement": "forbidden_if_changed_after_current_route_diagnosis_to_rescue_K2",
            "NullComparators": "must_not_be_dropped_after_inspection",
            "ValidationModes": "must_not_be_weakened_after_inspection",
            "SuccessCondition": "none",
            "WeakeningCondition": "none",
            "StrongNegativeCondition": "any use invalidates stronger interpretation",
            "CurrentAllowedToRun": False,
            "BlockingIssue": "post_hoc_rescue_route_forbidden",
            "ClaimBoundary": "locked_rerun_protocol_no_measurement_validation",
        },
    ]
    protocol = pd.DataFrame(protocol_rows)
    protocol.to_csv(OUT_PROTOCOL, index=False)

    preferred_ready = bool_text(upgrade["MeasurementValidationRouteAvailable"]) and bool_text(
        upgrade["PublicCovarianceStrongEnough"]
    )
    secondary_ready = bool_text(upgrade["BranchScatterPreflightAllowed"]) and False
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PUBLIC_COVARIANCE_LOCKED_RERUN_READINESS",
                "PreferredProtocol": "PCOV_RERUN_FULL_LIKELIHOOD_NATIVE_V1",
                "PreferredProtocolReady": preferred_ready,
                "SecondaryProtocol": "PCOV_RERUN_BRANCH_SCATTER_REGISTERED_V1",
                "SecondaryProtocolReady": secondary_ready,
                "ForbiddenProtocol": "PCOV_RERUN_FORBIDDEN_RESCUE_ROUTE",
                "AllowedCurrentRerunCount": int(preferred_ready) + int(secondary_ready),
                "MeasurementValidationStillBlocked": not preferred_ready,
                "PrimaryBlockingIssue": "full_public_covariance_transform_or_registered_shrinkage_route_missing",
                "NextAction": "complete public covariance upgrade queue before interpreting any stronger rerun",
                "Interpretation": "rerun_protocol_is_locked_but_no_stronger_public_covariance_rerun_is_currently_authorized",
                "ClaimBoundary": "locked_rerun_protocol_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_PROTOCOL}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
