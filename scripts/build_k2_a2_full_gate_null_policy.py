#!/usr/bin/env python3
"""Freeze the null-comparator policy for the K2 A2 full-gate preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "evidence" / "null_model_registry.csv"
SCORECARD_GUARD = ROOT / "evidence" / "source_split_likelihood_native_null_scorecard_readiness.csv"
SCORECARD = ROOT / "evidence" / "source_split_likelihood_native_null_scorecard.csv"
OUT_POLICY = ROOT / "evidence" / "k2_a2_full_gate_null_policy_v1.csv"
OUT_READINESS = ROOT / "evidence" / "k2_a2_full_gate_null_policy_readiness_v1.csv"

REQUIRED_NULLS = {
    "LCDM_NO_MEMORY",
    "GENERIC_POLYNOMIAL_SMOOTHING",
    "BACKREACTION_ONLY",
    "DYER_ROEDER_OPTICAL",
    "RECONSTRUCTION_ARTIFACT",
    "SIGN_RANDOMIZED_CONTROL",
    "COORDINATE_REMAP_CONTROL",
}


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def scorecard_allowed() -> bool:
    if not SCORECARD_GUARD.exists() or not SCORECARD.exists():
        return False
    guard = pd.read_csv(SCORECARD_GUARD)
    if guard.empty:
        return False
    return bool(
        guard.get("ScorecardAllowed", pd.Series([False])).map(truthy).all()
        and guard.get("ExternalK1Allowed", pd.Series([False])).map(truthy).all()
    )


def main() -> None:
    registry = pd.read_csv(REGISTRY)
    registry_ids = set(registry["NullID"].astype(str))
    missing = sorted(REQUIRED_NULLS - registry_ids)

    rows = []
    for _, row in registry.iterrows():
        null_id = str(row["NullID"])
        if null_id not in REQUIRED_NULLS:
            continue
        category = str(row["NullCategory"])
        physical_null = null_id in {"BACKREACTION_ONLY", "DYER_ROEDER_OPTICAL"}
        rows.append(
            {
                "PolicyID": "K2_A2_FULL_GATE_NULL_POLICY_V1",
                "NullID": null_id,
                "NullCategory": category,
                "RequiredForFullGatePreflight": True,
                "AllowedInPreflightScorecard": True,
                "AllowedForMeasurementValidation": False,
                "ValidationMode": (
                    "sensitivity_only_until_physical_calibration"
                    if physical_null
                    else "locked_comparator_same_vector_same_covariance"
                ),
                "FreeParameters": row["FreeParameters"],
                "RequiredComparison": row["RequiredComparison"],
                "BlockingIssue": (
                    "physical_null_amplitude_or_covariance_not_measurement_calibrated"
                    if physical_null
                    else ""
                ),
                "ClaimBoundary": "full_gate_null_policy_no_measurement_validation",
            }
        )
    policy = pd.DataFrame(rows)
    policy.to_csv(OUT_POLICY, index=False)

    has_required = not missing
    guard_ok = scorecard_allowed()
    policy_frozen = has_required and guard_ok
    readiness = pd.DataFrame(
        [
            {
                "PolicyID": "K2_A2_FULL_GATE_NULL_POLICY_V1",
                "RequiredNulls": len(REQUIRED_NULLS),
                "RegisteredRequiredNulls": len(REQUIRED_NULLS) - len(missing),
                "MissingRequiredNulls": ";".join(missing),
                "ScorecardGuardAllowed": guard_ok,
                "FullGateNullPolicyFrozen": policy_frozen,
                "AllowedForMeasurementValidation": False,
                "BlockingIssue": (
                    ""
                    if policy_frozen
                    else "required_nulls_missing_or_scorecard_guard_blocked"
                ),
                "NextAction": (
                    "Use frozen null policy in preflight reruns; keep physical nulls sensitivity-only until calibrated."
                    if policy_frozen
                    else "Register required nulls and enable scorecard guard before full-gate preflight rerun."
                ),
                "ClaimBoundary": "full_gate_null_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
