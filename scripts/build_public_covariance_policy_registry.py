#!/usr/bin/env python3
"""Register public covariance and cross-covariance policies for future reruns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

LOCKED_RERUN = ROOT / "evidence" / "public_covariance_locked_rerun_readiness.csv"
UPGRADE = ROOT / "evidence" / "public_covariance_upgrade_readiness.csv"
OUT_REGISTRY = ROOT / "evidence" / "public_covariance_policy_registry.csv"
OUT_READINESS = ROOT / "evidence" / "public_covariance_policy_readiness.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    locked = pd.read_csv(LOCKED_RERUN).iloc[0]
    upgrade = pd.read_csv(UPGRADE).iloc[0]

    registry_rows = [
        {
            "PolicyID": "PCOV_POLICY_FULL_PUBLIC_LIKELIHOOD_NATIVE_V1",
            "PolicyClass": "preferred_measurement_route",
            "CovarianceSource": "public_SN_BAO_likelihood_covariance",
            "CrossCovarianceRule": "derive_from_public_likelihood_or_joint_covariance_release",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "TuningAfterScorecardAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": True,
            "CurrentAvailable": False,
            "BlockingIssue": "full_likelihood_native_public_covariance_missing",
            "RequiredBeforeUse": "public covariance transform and cross-covariance rule must be frozen before scorecard execution",
            "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
        },
        {
            "PolicyID": "PCOV_POLICY_REGISTERED_SHRINKAGE_V1",
            "PolicyClass": "registered_public_benchmark_proxy",
            "CovarianceSource": "public_covariance_proxy_plus_predeclared_shrinkage",
            "CrossCovarianceRule": "predeclared_shrinkage_or_zero_cross_covariance_with_sensitivity_reported",
            "ShrinkageAllowed": True,
            "BranchScatterAllowed": False,
            "TuningAfterScorecardAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "registered_shrinkage_parameters_not_frozen_for_public_rerun",
            "RequiredBeforeUse": "lambda, correlation family, cross-covariance handling, and null policies must be frozen before rerun",
            "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
        },
        {
            "PolicyID": "PCOV_POLICY_ROW_ALIGNED_CROSS_COV_SENSITIVITY_V1",
            "PolicyClass": "sensitivity_only",
            "CovarianceSource": "public_proxy_with_row_aligned_cross_covariance_grid",
            "CrossCovarianceRule": "rho_cross_grid_used_only_for_sensitivity_not_selection",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "TuningAfterScorecardAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": True,
            "BlockingIssue": "cross_covariance_grid_is_not_likelihood_native",
            "RequiredBeforeUse": "must be reported as sensitivity and cannot select best rho_cross as the benchmark",
            "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
        },
        {
            "PolicyID": "PCOV_POLICY_BRANCH_SCATTER_REGISTERED_V1",
            "PolicyClass": "secondary_preflight_bridge",
            "CovarianceSource": "SN_BAO_branch_scatter_or_reconstruction_family_scatter",
            "CrossCovarianceRule": "not_applicable_unless_combined_with_public_covariance",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": True,
            "TuningAfterScorecardAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "branch_scatter_not_registered_as_independent_systematic_or_family_scatter",
            "RequiredBeforeUse": "declare whether branch scatter is systematic floor, reconstruction-family scatter, or sensitivity route",
            "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
        },
        {
            "PolicyID": "PCOV_POLICY_FORBIDDEN_TUNED_ROUTE",
            "PolicyClass": "forbidden",
            "CovarianceSource": "any_route_selected_after_K2_vs_control_score",
            "CrossCovarianceRule": "forbidden_if_tuned_to_make_K2_competitive",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "TuningAfterScorecardAllowed": False,
            "CanSupportPreflight": False,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "post_hoc_covariance_rescue_forbidden",
            "RequiredBeforeUse": "never allowed for stronger interpretation",
            "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
        },
    ]
    registry = pd.DataFrame(registry_rows)
    registry.to_csv(OUT_REGISTRY, index=False)

    eligible_preflight = registry[
        registry["CanSupportPreflight"].map(bool_text) & registry["CurrentAvailable"].map(bool_text)
    ]
    eligible_measurement = registry[
        registry["CanSupportMeasurementValidation"].map(bool_text) & registry["CurrentAvailable"].map(bool_text)
    ]
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PUBLIC_COVARIANCE_POLICY_READINESS",
                "PoliciesRegistered": len(registry),
                "CurrentlyAvailablePreflightPolicies": len(eligible_preflight),
                "CurrentlyAvailableMeasurementPolicies": len(eligible_measurement),
                "PreferredRerunReady": bool_text(locked["PreferredProtocolReady"]),
                "PublicCovarianceStrongEnough": bool_text(upgrade["PublicCovarianceStrongEnough"]),
                "MeasurementValidationRouteAvailable": bool_text(upgrade["MeasurementValidationRouteAvailable"]),
                "CurrentAllowedStrongerRerunCount": int(locked["AllowedCurrentRerunCount"]),
                "PrimaryAvailablePolicy": (
                    eligible_preflight.iloc[0]["PolicyID"] if len(eligible_preflight) else "NONE"
                ),
                "CurrentStatus": "SENSITIVITY_POLICY_AVAILABLE_STRONGER_POLICY_BLOCKED",
                "PrimaryBlockingIssue": "full_public_covariance_or_registered_shrinkage_policy_missing",
                "NextAction": "freeze registered shrinkage parameters or implement full likelihood-native public covariance",
                "Interpretation": "only sensitivity-level covariance policy is currently available; stronger rerun remains blocked",
                "ClaimBoundary": "public_covariance_policy_registry_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_REGISTRY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
