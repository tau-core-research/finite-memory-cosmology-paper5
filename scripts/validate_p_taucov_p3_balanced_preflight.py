#!/usr/bin/env python3
"""Validate the P-TauCov P3 balanced preflight artifact."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_preflight_summary.csv"
MATRIX = ROOT / "evidence/p_taucov_p3_balanced_preflight_matrix.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_PREFLIGHT_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_PREFLIGHT_READY_NO_CANDIDATE_NO_SCORING"


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
        print("P_TAUCOV_P3_BALANCED_PREFLIGHT_INVALID")
        return 1

    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()
    matrix = pd.read_csv(MATRIX)
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "no_target_residuals", bool(summary["UsesTargetResiduals"]) is False)
    add(rows, "no_score_outcome", bool(summary["UsesScoreOutcome"]) is False)
    add(rows, "not_candidate", bool(summary["CandidateConstructed"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "nonzero_balance_retention", float(summary["BalanceRetention"]) > 0.0)
    add(rows, "balanced_rank_positive", int(summary["BalancedRank"]) > 0)
    add(rows, "offdiag_structure_emitted", int(summary["OffDiagonalMatrixRows"]) > 0 and len(matrix) > 0)
    add(rows, "left_balance_leakage_small", float(summary["BalanceProjectorLeftLeakageFrobenius"]) < 1e-10)
    add(rows, "sandwich_balance_leakage_small", float(summary["BalanceProjectorSandwichLeakageFrobenius"]) < 1e-10)
    add(rows, "matrix_not_authorized_for_scoring", bool(matrix["ScoringAuthorized"].astype(bool).any()) is False)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    if bool(out["Passed"].all()):
        print("P_TAUCOV_P3_BALANCED_PREFLIGHT_VALID")
        return 0
    print("P_TAUCOV_P3_BALANCED_PREFLIGHT_INVALID")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
