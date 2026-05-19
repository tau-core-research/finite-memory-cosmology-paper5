#!/usr/bin/env python3
"""Register shrinkage parameters for a future preflight rerun.

This freezes a candidate parameter policy only. It does not run a scorecard and
does not authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SHRINKAGE_SUMMARY = ROOT / "evidence" / "source_split_joint_covariance_policy_summary.csv"
TEMPLATE_READINESS = ROOT / "evidence" / "registered_shrinkage_rerun_readiness.csv"
OUT_POLICY = ROOT / "evidence" / "registered_shrinkage_parameter_policy.csv"
OUT_READINESS = ROOT / "evidence" / "registered_shrinkage_parameter_policy_readiness.csv"


def main() -> None:
    shrink = pd.read_csv(SHRINKAGE_SUMMARY).iloc[0]
    template = pd.read_csv(TEMPLATE_READINESS).iloc[0]

    lambda_shrink = float(shrink["LambdaShrink"])
    correlation_length = float(shrink["CorrelationLength"])
    rho_sn_bao = float(shrink["RhoSNBAO"])

    policy_rows = [
        {
            "PolicyID": "REG_SHRINK_PARAM_BASELINE_V1",
            "PolicyRole": "primary_registered_future_preflight",
            "LambdaShrink": lambda_shrink,
            "CorrelationFamily": "exp_minus_abs_delta_x_over_L",
            "CorrelationLength": correlation_length,
            "RhoSNBAO": rho_sn_bao,
            "CrossCovariancePolicy": "zero_cross_covariance_primary_with_sensitivity_reported",
            "SourceArtifact": "evidence/source_split_joint_covariance_policy_summary.csv",
            "PositiveDefiniteInSourceArtifact": bool(shrink["PositiveDefinite"]),
            "SelectedAfterK2ScoreInspection": False,
            "MutableAfterRegistration": False,
            "CanSupportPreflightRerun": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAllowedToRun": False,
            "BlockingIssue": "locked_rerun_protocol_allows_zero_current_stronger_reruns",
            "RequiredReporting": "report public_proxy, registered_shrinkage, and cross_covariance_sensitivity without choosing best route after scoring",
            "ClaimBoundary": "registered_shrinkage_parameter_policy_no_measurement_validation",
        },
        {
            "PolicyID": "REG_SHRINK_PARAM_SENSITIVITY_GRID_V1",
            "PolicyRole": "sensitivity_only",
            "LambdaShrink": "0.0;0.05;0.10;0.15;0.25;0.35",
            "CorrelationFamily": "diagonal;nearest_neighbor;exp_z;exp_x;constant_offdiag",
            "CorrelationLength": "predeclared_grid_not_selection",
            "RhoSNBAO": "reported_grid_only",
            "CrossCovariancePolicy": "rho_cross_grid_reported_not_selected_as_benchmark",
            "SourceArtifact": "evidence/source_split_likelihood_native_cross_covariance_sensitivity.csv",
            "PositiveDefiniteInSourceArtifact": "filter_positive_definite_only",
            "SelectedAfterK2ScoreInspection": False,
            "MutableAfterRegistration": False,
            "CanSupportPreflightRerun": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAllowedToRun": False,
            "BlockingIssue": "sensitivity_grid_cannot_define_success_route",
            "RequiredReporting": "all grid outcomes must be reported; no best-grid promotion",
            "ClaimBoundary": "registered_shrinkage_parameter_policy_no_measurement_validation",
        },
        {
            "PolicyID": "REG_SHRINK_PARAM_FORBIDDEN_TUNED_V1",
            "PolicyRole": "forbidden",
            "LambdaShrink": "chosen_after_K2_vs_poly_score",
            "CorrelationFamily": "chosen_after_K2_vs_poly_score",
            "CorrelationLength": "chosen_after_K2_vs_poly_score",
            "RhoSNBAO": "chosen_after_K2_vs_poly_score",
            "CrossCovariancePolicy": "tuned_to_make_K2_competitive",
            "SourceArtifact": "none",
            "PositiveDefiniteInSourceArtifact": False,
            "SelectedAfterK2ScoreInspection": True,
            "MutableAfterRegistration": False,
            "CanSupportPreflightRerun": False,
            "CanSupportMeasurementValidation": False,
            "CurrentAllowedToRun": False,
            "BlockingIssue": "post_hoc_parameter_rescue_forbidden",
            "RequiredReporting": "invalid route",
            "ClaimBoundary": "registered_shrinkage_parameter_policy_no_measurement_validation",
        },
    ]
    policy = pd.DataFrame(policy_rows)
    policy.to_csv(OUT_POLICY, index=False)

    primary = policy[policy["PolicyID"].eq("REG_SHRINK_PARAM_BASELINE_V1")].iloc[0]
    template_only_before = int(template["TemplateOnlyComponents"])
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "REGISTERED_SHRINKAGE_PARAMETER_POLICY_READINESS",
                "PrimaryPolicyID": primary["PolicyID"],
                "PrimaryLambdaShrink": primary["LambdaShrink"],
                "PrimaryCorrelationFamily": primary["CorrelationFamily"],
                "PrimaryCorrelationLength": primary["CorrelationLength"],
                "PrimaryRhoSNBAO": primary["RhoSNBAO"],
                "PrimaryCrossCovariancePolicy": primary["CrossCovariancePolicy"],
                "ParameterPolicyRegistered": True,
                "CrossCovariancePolicyRegistered": True,
                "TemplateOnlyComponentsBeforePolicy": template_only_before,
                "TemplateOnlyComponentsAfterPolicy": 0,
                "CanSupportFuturePreflightRerun": True,
                "CurrentAllowedToRun": False,
                "MeasurementValidationAllowed": False,
                "PrimaryBlockingIssue": "locked_rerun_protocol_allows_zero_current_stronger_reruns",
                "NextAction": "update locked rerun readiness only after deciding whether to activate this registered shrinkage route for a future preflight",
                "Interpretation": "registered shrinkage parameters are frozen for future preflight but no current stronger rerun is authorized",
                "ClaimBoundary": "registered_shrinkage_parameter_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
