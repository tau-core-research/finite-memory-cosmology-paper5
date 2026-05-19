#!/usr/bin/env python3
"""Freeze the K2 A2 SN-BAO cross-covariance policy for preflight reruns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SENSITIVITY = ROOT / "evidence" / "source_split_likelihood_native_cross_covariance_summary.csv"
TRANSFORM_VERIFICATION = ROOT / "evidence" / "k2_a2_transform_covariance_verification_v1.csv"
OUT_POLICY = ROOT / "evidence" / "k2_a2_cross_covariance_policy_v1.csv"
OUT_READINESS = ROOT / "evidence" / "k2_a2_cross_covariance_policy_readiness_v1.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sensitivity_ready() -> tuple[bool, str]:
    if not SENSITIVITY.exists():
        return False, "cross_covariance_sensitivity_missing"
    sensitivity = pd.read_csv(SENSITIVITY)
    if sensitivity.empty:
        return False, "cross_covariance_sensitivity_empty"
    has_zero = bool((pd.to_numeric(sensitivity["RhoCross"]) == 0.0).any())
    rho_min = float(pd.to_numeric(sensitivity["RhoCross"]).min())
    rho_max = float(pd.to_numeric(sensitivity["RhoCross"]).max())
    return has_zero, f"rho_grid={rho_min}..{rho_max}; includes_zero={has_zero}; rows={len(sensitivity)}"


def transform_proxy_ready() -> tuple[bool, str]:
    if not TRANSFORM_VERIFICATION.exists():
        return False, "transform_covariance_verification_missing"
    verification = pd.read_csv(TRANSFORM_VERIFICATION)
    if verification.empty:
        return False, "transform_covariance_verification_empty"
    matches = bool(verification.get("MatchesReferenceWithinTolerance", pd.Series([False])).map(truthy).all())
    max_abs = verification.get("MaxAbsDifferenceVsReference", pd.Series([""])).iloc[0]
    return matches, f"transform_covariance_matches_reference={matches}; max_abs_diff={max_abs}"


def main() -> None:
    sens_ok, sens_obs = sensitivity_ready()
    transform_ok, transform_obs = transform_proxy_ready()

    policy = pd.DataFrame(
        [
            {
                "PolicyID": "K2_A2_CROSS_COVARIANCE_POLICY_V1",
                "PolicyClass": "registered_preflight_cross_covariance",
                "BenchmarkCrossCovarianceRule": "rho_cross_fixed_at_0_for_primary_preflight",
                "SensitivityRule": "row_aligned_rho_cross_grid_reported_without_best_rho_selection",
                "SensitivitySource": str(SENSITIVITY.relative_to(ROOT)),
                "TransformCovarianceSource": str(TRANSFORM_VERIFICATION.relative_to(ROOT)),
                "TuningAfterScorecardAllowed": False,
                "CanSupportPreflight": True,
                "CanSupportMeasurementValidation": False,
                "RequiredForUse": "report rho_cross=0 benchmark and full sensitivity grid; do not select rho_cross by K2 score",
                "ClaimBoundary": "cross_covariance_policy_no_measurement_validation",
            }
        ]
    )
    policy.to_csv(OUT_POLICY, index=False)

    ready = sens_ok and transform_ok
    readiness = pd.DataFrame(
        [
            {
                "PolicyID": "K2_A2_CROSS_COVARIANCE_POLICY_V1",
                "SensitivityReady": sens_ok,
                "TransformCovarianceReady": transform_ok,
                "PolicyFrozenForPreflight": ready,
                "AllowedForMeasurementValidation": False,
                "ObservedSensitivity": sens_obs,
                "ObservedTransformCovariance": transform_obs,
                "BlockingIssue": (
                    ""
                    if ready
                    else "cross_covariance_sensitivity_or_transform_covariance_missing"
                ),
                "NextAction": (
                    "Use declared rho_cross=0 benchmark with mandatory sensitivity grid in preflight reruns."
                    if ready
                    else "Build sensitivity and transform covariance verification before rerun."
                ),
                "ClaimBoundary": "cross_covariance_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
