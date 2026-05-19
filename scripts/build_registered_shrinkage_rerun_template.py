#!/usr/bin/env python3
"""Build a preregistered shrinkage route template for public-covariance reruns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

POLICY_READINESS = ROOT / "evidence" / "public_covariance_policy_readiness.csv"
LOCKED_RERUN = ROOT / "evidence" / "public_covariance_locked_rerun_readiness.csv"
OUT_TEMPLATE = ROOT / "evidence" / "registered_shrinkage_rerun_template.csv"
OUT_READINESS = ROOT / "evidence" / "registered_shrinkage_rerun_readiness.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    policy = pd.read_csv(POLICY_READINESS).iloc[0]
    locked = pd.read_csv(LOCKED_RERUN).iloc[0]

    template_rows = [
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "K2_OPERATOR",
            "LockedValue": "frozen/k2_operator_v1.yaml; W(x)=1+rho*x^3; p=3; rho<=4",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "LOCKED",
            "FailureIfMissingOrChanged": "post_hoc_kernel_change",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "K1_SOURCE",
            "LockedValue": "likelihood_native_joint_SN_BAO_no_memory_baseline_frozen_before_run",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "AVAILABLE_PREFLIGHT_BUT_NOT_MEASUREMENT_VALIDATING",
            "FailureIfMissingOrChanged": "post_hoc_K1_or_same_scorecard_rescue",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "COVARIANCE_ROUTE",
            "LockedValue": "registered_shrinkage_public_proxy; lambda; correlation_family; cross_covariance_policy frozen before run",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "TEMPLATE_ONLY_PARAMETERS_NOT_REGISTERED",
            "FailureIfMissingOrChanged": "post_hoc_covariance_route_selection",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "CROSS_COVARIANCE_POLICY",
            "LockedValue": "zero_cross_covariance_with_reported_sensitivity OR predeclared_shrinkage_cross_covariance",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "TEMPLATE_ONLY_POLICY_NOT_SELECTED",
            "FailureIfMissingOrChanged": "cross_covariance_tuned_to_help_K2",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "COORDINATE_MAPPING",
            "LockedValue": "likelihood_native_or_declared_coordinate_native_mapping frozen before run",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "AVAILABLE_PREFLIGHT",
            "FailureIfMissingOrChanged": "post_hoc_coordinate_rescue",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "NULL_COMPARATORS",
            "LockedValue": "K1_NO_MEMORY;POLY_DEG2;POLY_DEG3;ZERO_RESPONSE_CONTROL;SIGN_RANDOMIZED_CONTROL;COORDINATE_REMAP_CONTROL",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "TEMPLATE_LOCKED",
            "FailureIfMissingOrChanged": "dropped_control_after_inspection",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "VALIDATION_MODES",
            "LockedValue": "in_sample_AIC_BIC;leave_one_out;blocked_split;sign_stable_subset",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "TEMPLATE_LOCKED",
            "FailureIfMissingOrChanged": "weakened_validation_after_inspection",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
        {
            "TemplateID": "REG_SHRINK_RERUN_V1",
            "Component": "ACCEPTANCE_RULE",
            "LockedValue": "supportive if K2 improves over K1 and is competitive with polynomial controls under same covariance and validation policy",
            "MutableAfterRegistration": False,
            "RequiredBeforeRerun": True,
            "CurrentStatus": "TEMPLATE_LOCKED",
            "FailureIfMissingOrChanged": "post_hoc_success_definition",
            "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
        },
    ]
    template = pd.DataFrame(template_rows)
    template.to_csv(OUT_TEMPLATE, index=False)

    missing = template[
        template["CurrentStatus"].astype(str).str.contains("TEMPLATE_ONLY", na=False)
    ]
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "REGISTERED_SHRINKAGE_RERUN_TEMPLATE_READINESS",
                "TemplateID": "REG_SHRINK_RERUN_V1",
                "Components": len(template),
                "LockedComponents": int(
                    template["CurrentStatus"].astype(str).str.contains("LOCKED|AVAILABLE", regex=True).sum()
                ),
                "TemplateOnlyComponents": len(missing),
                "PolicyRegistryAvailablePreflightPolicies": int(policy["CurrentlyAvailablePreflightPolicies"]),
                "LockedRerunAllowedCurrentCount": int(locked["AllowedCurrentRerunCount"]),
                "TemplateCompleteForFutureRegistration": len(missing) == 0,
                "CurrentAllowedToRun": False,
                "MeasurementValidationAllowed": False,
                "PrimaryBlockingIssue": "shrinkage_parameters_and_cross_covariance_policy_not_registered",
                "NextAction": "choose and freeze shrinkage lambda, correlation family, and cross-covariance handling before any registered-shrinkage rerun",
                "Interpretation": "template exists but registered shrinkage route is not yet executable",
                "ClaimBoundary": "registered_shrinkage_template_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_TEMPLATE}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
