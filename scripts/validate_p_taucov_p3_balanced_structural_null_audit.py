#!/usr/bin/env python3
"""Validate the P3 balanced structural null audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_structural_null_audit.md"
OUT = ROOT / "evidence/p_taucov_p3_balanced_structural_null_audit_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING"
REQUIRED_NULLS = {
    "SIGN_FLIP",
    "ROW_REVERSE",
    "CLOCK_PHASE_SHIFT",
    "FAMILY_CYCLE",
    "SUPPORT_SHUFFLE",
    "RANDOM_SYMMETRIC_OFFDIAGONAL_MEDIAN",
    "RANDOM_SYMMETRIC_OFFDIAGONAL_MAXABS",
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
    for path in [TABLE, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_INVALID")
        return 1
    table = pd.read_csv(TABLE)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_pass", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "required_nulls_present", REQUIRED_NULLS.issubset(set(table["NullID"].astype(str))))
    add(rows, "no_target_residuals", bool(table["UsesTargetResiduals"].astype(bool).any()) is False)
    add(rows, "no_score_outcome", bool(table["UsesScoreOutcome"].astype(bool).any()) is False)
    add(rows, "scoring_not_authorized", bool(table["ScoringAuthorized"].astype(bool).any()) is False)
    add(rows, "summary_scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "sign_flip_is_orientation_control", set(table[table["NullID"].eq("SIGN_FLIP")]["NullClass"].astype(str)) == {"orientation_control_signed_not_abs_gate"})
    add(rows, "sign_flip_negative", float(summary["SignFlipCorrelation"]) < 0.0)
    add(rows, "structured_correlation_bounded", float(summary["MaxStructuredAbsCorrelation"]) < 0.95)
    add(rows, "random_median_correlation_bounded", float(summary["RandomMedianAbsCorrelation"]) < 0.25)
    add(rows, "doc_mentions_no_scoring", "authorizes no empirical scoring" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_VALID" if ok else "P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
