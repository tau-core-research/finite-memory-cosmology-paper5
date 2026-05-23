#!/usr/bin/env python3
"""Validate the P-TauCov parent-action scoring firewall."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_checklist.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_scoring_firewall.md"
OUT = ROOT / "evidence/p_taucov_parent_action_scoring_firewall_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_ACTION_SCORING_FIREWALL_VALIDATION"


def main() -> int:
    rows: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        rows.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [CHECKLIST, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [CHECKLIST, SUMMARY, DOC]):
        checklist = pd.read_csv(CHECKLIST)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_blocked", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_SCORING_BLOCKED_FREEZE_REQUIRED")
        add("parent_packet_pass", bool(summary["ParentActionPacketPass"]) is True)
        add("scoring_not_authorized", bool(summary["PTauCovScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("has_missing_freeze_items", int((~checklist["Satisfied"]).sum()) > 0)
        add("no_target_item_satisfied", bool(checklist.loc[checklist["ItemID"].eq("NO_TARGET_OR_SCORE_INPUTS"), "Satisfied"].iloc[0]) is True)
        add("doc_contains_no_scoring_boundary", "no empirical scoring" in doc and "no survival claim" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_SCORING_FIREWALL_VALID" if ok else "P_TAUCOV_PARENT_ACTION_SCORING_FIREWALL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
