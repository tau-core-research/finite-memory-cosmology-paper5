#!/usr/bin/env python3
"""Validate the candidate full parent-action packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet.csv"
GATES = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_summary.csv"
DOC = ROOT / "docs/p_taucov_candidate_full_parent_action_packet.md"
OUT = ROOT / "evidence/p_taucov_candidate_full_parent_action_packet_validation.csv"

AUDIT_ID = "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_VALIDATION"
EXPECTED_BLOCKERS = {
    "COVARIANCE_MAP",
    "REFERENCE_BACKGROUND",
    "S_REST",
}


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

    for path in [PACKET, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [PACKET, GATES, SUMMARY, DOC]):
        packet = pd.read_csv(PACKET)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        blockers = set(str(summary["BlockingFields"]).split(";"))
        add("status_blocked_no_scoring", str(summary["Status"]).endswith("BLOCKED_NO_SCORING"))
        add("has_failed_embedding_gates", int((~gates["Passed"]).sum()) > 0)
        add("expected_blockers", blockers == EXPECTED_BLOCKERS)
        add("gates_match_summary", int(gates["Passed"].sum()) == int(summary["GatesPassed"]))
        add("partial_fields_match_summary", int(packet["DeclarationStatus"].eq("partial").sum()) == int(summary["PartialFields"]))
        add("scoring_not_authorized", not bool(packet["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(packet["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(packet["UsesScoreOutcome"].any()))
        add("doc_contains_blocking_fields", "Blocking Fields" in doc)
        add("doc_contains_not_full_action", "not a full Tau Core action" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_VALID" if ok else "P_TAUCOV_CANDIDATE_FULL_PARENT_ACTION_PACKET_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
