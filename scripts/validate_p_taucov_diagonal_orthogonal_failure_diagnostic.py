#!/usr/bin/env python3
"""Validate the diagonal-orthogonal P-TauCov failure diagnostic."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AGG = ROOT / "evidence/p_taucov_diagonal_orthogonal_failure_aggregate_diagnostic.csv"
FOLD = ROOT / "evidence/p_taucov_diagonal_orthogonal_failure_fold_diagnostic.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_scorecard_summary.csv"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_failure_diagnostic_validation.csv"

AUDIT_ID = "P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_CLOCK_AND_FAMILY_FAILURE_LOCALIZED_NO_NEW_SCORING"


def check(check_id: str, passed: bool, rows: list[dict], required: bool = True) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": bool(required),
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    check(f"exists_{AGG.relative_to(ROOT)}", AGG.exists(), rows)
    check(f"exists_{FOLD.relative_to(ROOT)}", FOLD.exists(), rows)
    check(f"exists_{SUMMARY.relative_to(ROOT)}", SUMMARY.exists(), rows)
    if not (AGG.exists() and FOLD.exists() and SUMMARY.exists()):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_INVALID")
        return 1

    agg = pd.read_csv(AGG).iloc[0].to_dict()
    fold = pd.read_csv(FOLD)
    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()

    check("status_expected", str(agg["Status"]) == EXPECTED_STATUS, rows)
    check("no_survival_claim", bool(agg["SurvivalClaimAuthorized"]) is False, rows)
    check("no_tau_validation_claim", bool(agg["TauCoreValidationClaimAuthorized"]) is False, rows)
    check(
        "primary_beats_null_matches_summary",
        bool(agg["PrimaryBeatsNullMax"])
        == (float(summary["PrimarySignedS"]) > float(summary["RequiredNullMaxSignedS"])),
        rows,
    )
    check(
        "clock_failure_detected",
        float(agg["ClockSignedS"]) < 0.0 and int(agg["ClockNegativeBlockCount"]) >= 1,
        rows,
    )
    check(
        "family_dominance_detected",
        float(agg["DominantPositiveFamilyShare"]) > 0.5,
        rows,
    )
    check(
        "fold_diagnostic_has_primary_family_clock_groups",
        {"primary_family", "primary_clock", "secondary_family_x_clock"}.issubset(set(fold["FoldGroup"].astype(str))),
        rows,
    )
    check(
        "next_gate_is_prescoring_gate",
        str(agg["NextGate"]) == "predeclared_clock_consistent_family_balanced_support_required",
        rows,
    )

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    if bool(out[out["Required"]]["Passed"].all()):
        print("P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_VALID")
        return 0
    print("P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_INVALID")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
