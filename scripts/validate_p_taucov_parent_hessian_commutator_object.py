#!/usr/bin/env python3
"""Validate the parent-Hessian/commutator object packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OBJECT = ROOT / "evidence/p_taucov_parent_hessian_commutator_object.csv"
GATES = ROOT / "evidence/p_taucov_parent_hessian_commutator_object_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_hessian_commutator_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_hessian_commutator_object.md"
OUT = ROOT / "evidence/p_taucov_parent_hessian_commutator_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_VALIDATION"


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

    for path in [OBJECT, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if OBJECT.exists() and GATES.exists() and SUMMARY.exists() and DOC.exists():
        obj = pd.read_csv(OBJECT)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_no_scoring", str(summary["Status"]).endswith("NO_SCORING"))
        add("scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
        add("scoring_not_authorized_object", not bool(obj["ScoringAuthorized"].any()))
        add("uses_no_target_residuals", not bool(obj["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(obj["UsesScoreOutcome"].any()))
        add("gates_match_summary", int(gates["Passed"].sum()) == int(summary["GatesPassed"]))
        add("has_projection_failure", bool((gates["GateID"].eq("HC-G3_LOW_PROJECTION_NULL_CORRELATION") & ~gates["Passed"]).any()))
        add("morphology_gate_passed", bool((gates["GateID"].eq("HC-G2_LOW_MORPHOLOGY_NULL_CORRELATION") & gates["Passed"]).any()))
        add("doc_contains_not_measurement_validation", "not measurement" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_VALID" if ok else "P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
