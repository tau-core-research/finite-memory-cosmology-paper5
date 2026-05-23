#!/usr/bin/env python3
"""Validate Q-native branch-response curvature preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_v1"


def main() -> int:
    required = [
        EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_summary.csv",
        EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_gates.csv",
        EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_matrix.csv",
        EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_vector.csv",
        DOCS / "p_taucov_q_native_branch_response_curvature_preflight.md",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required artifact: {path}")
    summary = pd.read_csv(required[0])
    gates = pd.read_csv(required[1])
    if len(summary) != 1:
        raise SystemExit("Expected one summary row")
    row = summary.iloc[0]
    if row["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    if bool(row["ScoringAuthorized"]) or bool(row["SurvivalClaimAuthorized"]) or bool(row["TauCoreValidationClaimAuthorized"]):
        raise SystemExit("Preflight must not authorize scoring, survival, or Tau validation")
    passed = int(gates["Passed"].astype(bool).sum())
    total = int(len(gates))
    if int(row["PassedGates"]) != passed or int(row["TotalGates"]) != total:
        raise SystemExit("Gate count mismatch")
    expected = (
        "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_PASS_NO_SCORING"
        if passed == total
        else "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_FAIL_NO_SCORING"
    )
    if row["Status"] != expected:
        raise SystemExit(f"Unexpected status: {row['Status']} != {expected}")
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_VALID",
                "PreflightStatus": row["Status"],
                "PassedGates": passed,
                "TotalGates": total,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_q_native_branch_response_curvature_preflight_validation.csv", index=False)
    print("P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
