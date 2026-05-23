#!/usr/bin/env python3
"""Validate the P-TauCov clock/family-balanced next gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "evidence/p_taucov_clock_family_balanced_next_gate.csv"
OUT = ROOT / "evidence/p_taucov_clock_family_balanced_next_gate_validation.csv"

AUDIT_ID = "P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_NEXT_GATE_DEFINED_NO_CANDIDATE_NO_SCORING"
REQUIRED = {
    "parent_derived_support",
    "clock_consistency",
    "family_balance",
    "diagonal_orthogonality",
    "null_reuse_discipline",
    "forbidden_failure_tuning",
    "claim_boundary",
}


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": True,
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    add(rows, f"exists_{GATE.relative_to(ROOT)}", GATE.exists())
    if not GATE.exists():
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_INVALID")
        return 1
    df = pd.read_csv(GATE)
    add(rows, "status_expected", set(df["Status"].astype(str)) == {EXPECTED_STATUS})
    add(rows, "all_required_gates_present", REQUIRED.issubset(set(df["Requirement"].astype(str))))
    add(rows, "all_gates_required", bool(df["Required"].astype(bool).all()))
    add(rows, "no_scoring_authorized_by_status", "NO_CANDIDATE_NO_SCORING" in str(df["Status"].iloc[0]))
    add(rows, "forbidden_failure_tuning_declared", "forbidden_failure_tuning" in set(df["Requirement"].astype(str)))
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    if bool(out["Passed"].all()):
        print("P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_VALID")
        return 0
    print("P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_INVALID")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
