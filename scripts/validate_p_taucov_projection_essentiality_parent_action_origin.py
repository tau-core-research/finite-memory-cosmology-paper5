#!/usr/bin/env python3
"""Validate the projection-essentiality parent-action origin packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_terms.csv"
HESSIAN = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_hessian.csv"
GATES = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_parent_action_origin_packet.md"
OUT = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_VALIDATION"


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
        add("hessian_matches_witness", float(summary["MaxAbsHessianMinusWitness"]) < 1e-12)
        add("projection_essentiality_high", float(summary["ProjectionEssentiality"]) > 0.40)
        add("term_count_three", len(terms) == 3)
        add("terms_use_no_target_residuals", not bool(terms["UsesTargetResiduals"].any()))
        add("terms_use_no_score_outcome", not bool(terms["UsesScoreOutcome"].any()))
        add("hessian_use_no_target_residuals", not bool(hessian["UsesTargetResiduals"].any()))
        add("scoring_not_authorized", not bool(terms["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("doc_contains_normal_form", "V_{\\rm PE}" in doc)
        add("doc_contains_forbidden_claim", "not a completed Tau Core action" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_VALID" if ok else "P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
