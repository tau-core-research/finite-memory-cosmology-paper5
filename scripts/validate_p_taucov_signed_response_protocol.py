#!/usr/bin/env python3
"""Validate signed-response protocol for branch-localized P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_signed_response_protocol.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_protocol.md"
OUT = ROOT / "evidence/p_taucov_signed_response_protocol_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_ready_for_manifest", str(summary["Status"]) == "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_FROZEN_READY_FOR_MANIFEST_NO_SCORING")
        add("signed_required", bool(table.loc[table["RuleID"].eq("SR-01_SIGNED_MAP_REQUIRED"), "Satisfied"].iloc[0]) is True)
        add("no_rescue_rule", bool(table.loc[table["RuleID"].eq("SR-05_NO_SURVIVAL_RESCUE"), "Satisfied"].iloc[0]) is True)
        add("statistic_freeze_present", bool(table.loc[table["RuleID"].eq("SR-02_STATISTIC"), "Satisfied"].iloc[0]) is True)
        add("null_policy_present", bool(table.loc[table["RuleID"].eq("SR-03_NULLS"), "Satisfied"].iloc[0]) is True)
        add("aggregation_policy_present", bool(table.loc[table["RuleID"].eq("SR-04_AGGREGATION"), "Satisfied"].iloc[0]) is True)
        add("all_rules_satisfied", bool(table["Satisfied"].all()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_says_not_covariance", "not a covariance likelihood claim" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_VALID" if ok else "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
