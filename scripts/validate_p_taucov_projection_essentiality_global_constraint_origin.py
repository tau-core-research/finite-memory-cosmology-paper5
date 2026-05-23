#!/usr/bin/env python3
"""Validate the P-TauCov global constraint-origin packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_map.csv"
GATES = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_global_constraint_origin_packet.md"
OUT = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_VALIDATION"


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

    for path in [MAP, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MAP, GATES, SUMMARY, DOC]):
        mapping = pd.read_csv(MAP)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("seven_parent_principles", int(summary["ParentPrinciplesDeclared"]) == 7)
        add("seven_local_constraints", int(summary["LocalConstraintsMapped"]) == 7)
        add("one_to_one_mapping", mapping["ParentPrincipleID"].nunique() == mapping["LocalConstraintID"].nunique() == len(mapping))
        add("normal_form_coefficients_inherited", float(summary["SelectedPB"]) == -2.0 and float(summary["SelectedPPhi"]) == -1.0 and float(summary["SelectedB2"]) == -0.5)
        add("uses_no_target_residuals", not bool(mapping["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(mapping["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(mapping["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("doc_contains_not_final_action", "not a final" in doc and "microscopic" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_VALID" if ok else "P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
