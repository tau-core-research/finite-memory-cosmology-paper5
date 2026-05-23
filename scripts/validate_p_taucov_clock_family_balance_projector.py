#!/usr/bin/env python3
"""Validate the P-TauCov clock/family balance projector."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence/p_taucov_clock_family_balance_projector_summary.csv"
MATRIX = ROOT / "evidence/p_taucov_clock_family_balance_projector_matrix.csv"
OUT = ROOT / "evidence/p_taucov_clock_family_balance_projector_validation.csv"

AUDIT_ID = "P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_BALANCE_PROJECTOR_FROZEN_NO_CANDIDATE_NO_SCORING"
TOL = 1e-10


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
    add(rows, f"exists_{SUMMARY.relative_to(ROOT)}", SUMMARY.exists())
    add(rows, f"exists_{MATRIX.relative_to(ROOT)}", MATRIX.exists())
    if not (SUMMARY.exists() and MATRIX.exists()):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_INVALID")
        return 1

    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "not_candidate", bool(summary["CandidateConstructed"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "no_target_residuals", bool(summary["UsesTargetResiduals"]) is False)
    add(rows, "no_score_outcome", bool(summary["UsesScoreOutcome"]) is False)
    add(rows, "symmetric", float(summary["SymmetryErrorFrobenius"]) <= TOL)
    add(rows, "idempotent", float(summary["IdempotenceErrorFrobenius"]) <= TOL)
    add(rows, "annihilates_family_indicators", float(summary["FamilyIndicatorLeakageFrobenius"]) <= TOL)
    add(rows, "annihilates_clock_indicators", float(summary["ClockIndicatorLeakageFrobenius"]) <= TOL)
    add(rows, "annihilates_intercept", float(summary["InterceptLeakageFrobenius"]) <= TOL)
    add(rows, "rank_positive", int(summary["ProjectorRank"]) > 0)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    if bool(out["Passed"].all()):
        print("P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_VALID")
        return 0
    print("P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_INVALID")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
