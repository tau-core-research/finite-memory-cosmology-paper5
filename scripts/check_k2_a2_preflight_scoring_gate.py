#!/usr/bin/env python3
"""Check whether the locked K2 A2 preflight scorecard may be rerun."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FULL_GATE = ROOT / "evidence" / "k2_a2_full_likelihood_gate_readiness.csv"
TRANSFORM_READY = ROOT / "evidence" / "k2_a2_transform_matrix_readiness_v1.csv"
TRANSFORM_COV = ROOT / "evidence" / "k2_a2_transform_covariance_verification_v1.csv"
K1_READY = ROOT / "evidence" / "source_split_likelihood_native_k1_readiness.csv"
NULL_READY = ROOT / "evidence" / "k2_a2_full_gate_null_policy_readiness_v1.csv"
CROSS_READY = ROOT / "evidence" / "k2_a2_cross_covariance_policy_readiness_v1.csv"

OUT = ROOT / "evidence" / "k2_a2_preflight_scoring_gate.csv"
SUMMARY = ROOT / "evidence" / "k2_a2_preflight_scoring_gate_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def row(rows: list[dict[str, object]], check_id: str, ok: bool, observed: str, issue: str, action: str) -> None:
    rows.append(
        {
            "GateID": "K2_A2_PREFLIGHT_SCORING_GATE_V1",
            "CheckID": check_id,
            "Status": "PASS" if ok else "BLOCKED",
            "Observed": observed,
            "BlockingIssue": "" if ok else issue,
            "NextAction": action,
            "ClaimBoundary": "preflight_scoring_gate_no_measurement_validation",
        }
    )


def full_gate_input_status() -> tuple[bool, str]:
    if not FULL_GATE.exists():
        return False, "full_gate_readiness_missing"
    gate = pd.read_csv(FULL_GATE)
    required = gate[gate["GateClass"].eq("required")]
    ids = {
        "A2_FULL_GATE_SN_PUBLIC_INPUT",
        "A2_FULL_GATE_BAO_PUBLIC_INPUT",
        "A2_FULL_GATE_LOCKED_PREDICTION",
    }
    subset = required[required["GateID"].isin(ids)]
    ok = len(subset) == len(ids) and bool((subset["Status"] == "PASS").all())
    return ok, f"passed_inputs={int((subset['Status'] == 'PASS').sum())}/{len(ids)}"


def transform_status() -> tuple[bool, str]:
    if not TRANSFORM_READY.exists() or not TRANSFORM_COV.exists():
        return False, "transform_readiness_or_covariance_verification_missing"
    ready = pd.read_csv(TRANSFORM_READY).iloc[0]
    cov = pd.read_csv(TRANSFORM_COV).iloc[0]
    ok = truthy(ready["TransformMatricesFrozen"]) and truthy(cov["MatchesReferenceWithinTolerance"])
    return ok, (
        f"matrices_frozen={ready['TransformMatricesFrozen']}; "
        f"covariance_reproduced={cov['MatchesReferenceWithinTolerance']}; "
        f"max_abs_diff={cov['MaxAbsDifferenceVsReference']}"
    )


def k1_status() -> tuple[bool, str]:
    if not K1_READY.exists():
        return False, "k1_readiness_missing"
    k1 = pd.read_csv(K1_READY).iloc[0]
    ok = truthy(k1["LikelihoodNativeK1ExportAllowed"])
    return ok, f"k1_allowed={k1['LikelihoodNativeK1ExportAllowed']}; decision={k1['CurrentDecision']}"


def null_status() -> tuple[bool, str]:
    if not NULL_READY.exists():
        return False, "null_policy_readiness_missing"
    nulls = pd.read_csv(NULL_READY).iloc[0]
    ok = truthy(nulls["FullGateNullPolicyFrozen"])
    return ok, f"null_policy_frozen={nulls['FullGateNullPolicyFrozen']}; registered={nulls['RegisteredRequiredNulls']}/{nulls['RequiredNulls']}"


def cross_status() -> tuple[bool, str]:
    if not CROSS_READY.exists():
        return False, "cross_covariance_policy_readiness_missing"
    cross = pd.read_csv(CROSS_READY).iloc[0]
    ok = truthy(cross["PolicyFrozenForPreflight"])
    return ok, f"cross_policy_frozen={cross['PolicyFrozenForPreflight']}; sensitivity={cross['SensitivityReady']}"


def main() -> None:
    rows: list[dict[str, object]] = []
    checks = [
        ("PUBLIC_INPUTS_AND_LOCKED_A2", full_gate_input_status),
        ("FROZEN_TRANSFORMS_AND_COVARIANCE_REPRODUCTION", transform_status),
        ("PROMOTED_K1_PREFLIGHT_BASELINE", k1_status),
        ("FROZEN_NULL_POLICY", null_status),
        ("FROZEN_CROSS_COVARIANCE_PREFLIGHT_POLICY", cross_status),
    ]
    for check_id, fn in checks:
        ok, observed = fn()
        row(
            rows,
            check_id,
            ok,
            observed,
            f"{check_id.lower()}_blocked",
            "Repair or freeze this preflight component before rerunning the A2 scorecard.",
        )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    passed = int((output["Status"] == "PASS").sum())
    total = len(output)
    allowed = passed == total
    summary = pd.DataFrame(
        [
            {
                "GateID": "K2_A2_PREFLIGHT_SCORING_GATE_V1",
                "Checks": total,
                "PassedChecks": passed,
                "PreflightScorecardAllowed": allowed,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "PREFLIGHT_SCORECARD_ALLOWED_NOT_MEASUREMENT_VALIDATION"
                    if allowed
                    else "PREFLIGHT_SCORECARD_BLOCKED"
                ),
                "NextAction": (
                    "Rerun locked A2/K1/null scorecard using frozen preflight transforms and policies."
                    if allowed
                    else "Clear blocked preflight checks before rerun."
                ),
                "ClaimBoundary": "preflight_scoring_gate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
