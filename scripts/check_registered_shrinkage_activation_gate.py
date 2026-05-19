#!/usr/bin/env python3
"""Check whether the registered-shrinkage route may be activated for preflight.

This gate does not run a scorecard. It only determines whether the already
registered shrinkage parameter policy is complete enough to permit a future
preflight rerun under the locked public-covariance rerun protocol.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

PARAM_POLICY = ROOT / "evidence" / "registered_shrinkage_parameter_policy_readiness.csv"
LOCKED_RERUN = ROOT / "evidence" / "public_covariance_locked_rerun_readiness.csv"
UPGRADE = ROOT / "evidence" / "public_covariance_upgrade_readiness.csv"
POLICY_REGISTRY = ROOT / "evidence" / "public_covariance_policy_readiness.csv"

OUT_GATE = ROOT / "evidence" / "registered_shrinkage_activation_gate.csv"
OUT_SUMMARY = ROOT / "evidence" / "registered_shrinkage_activation_summary.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    param = pd.read_csv(PARAM_POLICY).iloc[0]
    locked = pd.read_csv(LOCKED_RERUN).iloc[0]
    upgrade = pd.read_csv(UPGRADE).iloc[0]
    registry = pd.read_csv(POLICY_REGISTRY).iloc[0]

    checks = [
        {
            "CheckID": "ACT_1_PARAMETER_POLICY_REGISTERED",
            "Requirement": "Shrinkage parameter policy is registered before rerun.",
            "Passed": bool_text(param["ParameterPolicyRegistered"]),
            "BlocksPreflightActivation": True,
            "BlocksMeasurementValidation": True,
            "Evidence": "registered_shrinkage_parameter_policy_readiness.csv",
        },
        {
            "CheckID": "ACT_2_CROSS_COV_POLICY_REGISTERED",
            "Requirement": "Cross-covariance policy is registered before rerun.",
            "Passed": bool_text(param["CrossCovariancePolicyRegistered"]),
            "BlocksPreflightActivation": True,
            "BlocksMeasurementValidation": True,
            "Evidence": "registered_shrinkage_parameter_policy_readiness.csv",
        },
        {
            "CheckID": "ACT_3_TEMPLATE_COMPLETE",
            "Requirement": "Registered-shrinkage template has no template-only components.",
            "Passed": int(param["TemplateOnlyComponentsAfterPolicy"]) == 0,
            "BlocksPreflightActivation": True,
            "BlocksMeasurementValidation": True,
            "Evidence": "registered_shrinkage_parameter_policy_readiness.csv",
        },
        {
            "CheckID": "ACT_4_K2_VS_K1_SUPPORTIVE",
            "Requirement": "Support ladder remains positive for K2-vs-K1.",
            "Passed": bool_text(upgrade["K2VsK1Supportive"]),
            "BlocksPreflightActivation": False,
            "BlocksMeasurementValidation": True,
            "Evidence": "public_covariance_upgrade_readiness.csv",
        },
        {
            "CheckID": "ACT_5_K2_VS_POLY_RESOLVED",
            "Requirement": "K2-vs-polynomial objection is resolved before measurement validation.",
            "Passed": bool_text(upgrade["K2VsPolynomialResolved"]),
            "BlocksPreflightActivation": False,
            "BlocksMeasurementValidation": True,
            "Evidence": "public_covariance_upgrade_readiness.csv",
        },
        {
            "CheckID": "ACT_6_PUBLIC_MEASUREMENT_ROUTE_AVAILABLE",
            "Requirement": "Full public measurement route is available.",
            "Passed": bool_text(upgrade["MeasurementValidationRouteAvailable"]),
            "BlocksPreflightActivation": False,
            "BlocksMeasurementValidation": True,
            "Evidence": "public_covariance_upgrade_readiness.csv",
        },
        {
            "CheckID": "ACT_7_STRONGER_RERUN_CURRENTLY_LOCKED",
            "Requirement": "Locked rerun protocol currently allows zero stronger reruns.",
            "Passed": int(locked["AllowedCurrentRerunCount"]) == 0,
            "BlocksPreflightActivation": False,
            "BlocksMeasurementValidation": False,
            "Evidence": "public_covariance_locked_rerun_readiness.csv",
        },
        {
            "CheckID": "ACT_8_POLICY_REGISTRY_HAS_ONLY_SENSITIVITY_AVAILABLE",
            "Requirement": "Policy registry still has no measurement-grade covariance policy.",
            "Passed": int(registry["CurrentlyAvailableMeasurementPolicies"]) == 0,
            "BlocksPreflightActivation": False,
            "BlocksMeasurementValidation": True,
            "Evidence": "public_covariance_policy_readiness.csv",
        },
    ]
    gate = pd.DataFrame(checks)
    gate["ClaimBoundary"] = "registered_shrinkage_activation_gate_no_measurement_validation"
    gate.to_csv(OUT_GATE, index=False)

    preflight_blockers = gate[
        gate["BlocksPreflightActivation"].map(bool_text) & ~gate["Passed"].map(bool_text)
    ]
    measurement_blockers = gate[
        gate["BlocksMeasurementValidation"].map(bool_text) & ~gate["Passed"].map(bool_text)
    ]
    preflight_allowed = len(preflight_blockers) == 0
    summary = pd.DataFrame(
        [
            {
                "GateID": "REGISTERED_SHRINKAGE_ACTIVATION_GATE",
                "Checks": len(gate),
                "PassedChecks": int(gate["Passed"].map(bool_text).sum()),
                "PreflightBlockingChecks": len(preflight_blockers),
                "MeasurementBlockingChecks": len(measurement_blockers),
                "RegisteredShrinkagePreflightActivationAllowed": preflight_allowed,
                "RegisteredShrinkageMeasurementValidationAllowed": False,
                "AllowedRerunType": "future_preflight_only" if preflight_allowed else "none",
                "CurrentScorecardShouldRunNow": False,
                "PrimaryPreflightBlocker": (
                    "none" if preflight_allowed else str(preflight_blockers.iloc[0]["CheckID"])
                ),
                "PrimaryMeasurementBlocker": (
                    "none" if len(measurement_blockers) == 0 else str(measurement_blockers.iloc[0]["CheckID"])
                ),
                "NextAction": "if desired, create a separate future-preflight run script that consumes the registered shrinkage policy without changing K2 or K1",
                "Interpretation": (
                    "registered shrinkage route can be activated for future preflight only; "
                    "measurement validation remains blocked"
                    if preflight_allowed
                    else "registered shrinkage route is still blocked even for future preflight"
                ),
                "ClaimBoundary": "registered_shrinkage_activation_gate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_GATE}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
