#!/usr/bin/env python3
"""Validate the minimal global parent-action scaffold packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_terms.csv"
HESSIAN = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_hessian.csv"
GATES = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_summary.csv"
DOC = ROOT / "docs/p_taucov_minimal_global_parent_action_scaffold_packet.md"
OUT = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_validation.csv"

AUDIT_ID = "P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TERMS, HESSIAN, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TERMS, HESSIAN, GATES, SUMMARY, DOC]):
        terms = pd.read_csv(TERMS)
        hessian = pd.read_csv(HESSIAN)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("active_term_count_three", int(summary["ActiveTermCount"]) == 3 and len(terms) == 3)
        add("branch_response_minus_two", abs(float(summary["BranchResponseBStarOverP"]) + 2.0) < 1e-12)
        add("hessian_matches_witness", float(summary["MaxAbsHessianMinusWitness"]) < 1e-12)
        add("uses_no_target_residuals", not bool(terms["UsesTargetResiduals"].any()) and not bool(hessian["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(terms["UsesScoreOutcome"].any()) and not bool(hessian["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(terms["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("doc_contains_not_final_action", "not a final microscopic Tau Core action" in doc)
        add("doc_contains_not_measurement_validation", "measurement validation" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_VALID" if ok else "P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
