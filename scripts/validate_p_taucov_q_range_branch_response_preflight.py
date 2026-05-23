#!/usr/bin/env python3
"""Validate Q-range branch-response preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_v1"


def main():
    paths = [
        EVIDENCE / "p_taucov_q_range_branch_response_preflight_summary.csv",
        EVIDENCE / "p_taucov_q_range_branch_response_preflight_gates.csv",
        EVIDENCE / "p_taucov_q_range_branch_response_preflight_matrix.csv",
        DOCS / "p_taucov_q_range_branch_response_preflight.md",
    ]
    for p in paths:
        if not p.exists():
            raise SystemExit(f"Missing artifact: {p}")
    s = pd.read_csv(paths[0])
    g = pd.read_csv(paths[1])
    if len(s) != 1:
        raise SystemExit("Expected one summary row")
    row = s.iloc[0]
    if row["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    for col in ["ScoringAuthorized", "SurvivalClaimAuthorized", "TauCoreValidationClaimAuthorized"]:
        if bool(row[col]):
            raise SystemExit(f"{col} must be false")
    passed = int(g["Passed"].astype(bool).sum())
    total = len(g)
    expected = "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_PASS_NO_SCORING" if passed == total else "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_FAIL_NO_SCORING"
    if row["Status"] != expected:
        raise SystemExit("Unexpected status")
    pd.DataFrame([{
        "FreezeID": FREEZE_ID,
        "ValidationStatus": "P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_VALID",
        "PreflightStatus": row["Status"],
        "PassedGates": passed,
        "TotalGates": total,
        "ScoringAuthorized": False,
    }]).to_csv(EVIDENCE / "p_taucov_q_range_branch_response_preflight_validation.csv", index=False)
    print("P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_VALID")


if __name__ == "__main__":
    main()
