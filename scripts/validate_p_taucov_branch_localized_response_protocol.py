#!/usr/bin/env python3
"""Validate the P-TauCov branch-localized response protocol declaration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_branch_localized_response_protocol.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_response_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_response_protocol.md"
OUT = ROOT / "evidence/p_taucov_branch_localized_response_protocol_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_blocked_no_scoring", str(summary["Status"]) == "P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_DECLARED_BLOCKED_NO_SCORING")
        add("has_missing_gates", int(summary["SatisfiedGates"]) < int(summary["TotalGates"]))
        add("route_trigger_satisfied", bool(table.loc[table["GateID"].eq("BLR-01_ROUTE_TRIGGER"), "Satisfied"].iloc[0]) is True)
        add("no_rescue_rule_satisfied", bool(table.loc[table["GateID"].eq("BLR-06_NO_RESCUE_RULE"), "Satisfied"].iloc[0]) is True)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(table["UsesScoreOutcome"].any()))
        add("doc_mentions_not_v4", "not a v4 score search" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_VALID" if ok else "P_TAUCOV_BRANCH_LOCALIZED_RESPONSE_PROTOCOL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
