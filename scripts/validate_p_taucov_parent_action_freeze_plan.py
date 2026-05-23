#!/usr/bin/env python3
"""Validate the P-TauCov parent-action freeze plan."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "evidence/p_taucov_parent_action_freeze_plan.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_freeze_plan_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_freeze_plan.md"
OUT = ROOT / "evidence/p_taucov_parent_action_freeze_plan_validation.csv"


def main() -> int:
    rows: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        rows.append({"AuditID": "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [PLAN, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [PLAN, SUMMARY, DOC]):
        plan = pd.read_csv(PLAN)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_declared", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_DECLARED_NO_SCORING")
        add("six_steps", len(plan) == 6)
        add("none_completed", int(plan["Completed"].sum()) == 0)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(plan["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(plan["UsesScoreOutcome"].any()))
        add("doc_has_boundary", "does not authorize scoring" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_VALID" if ok else "P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
