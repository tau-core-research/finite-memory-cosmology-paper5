#!/usr/bin/env python3
"""Validate signed-response blocked aggregation policy for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_signed_response_aggregation_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_aggregation_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_aggregation_policy.md"
OUT = ROOT / "evidence/p_taucov_signed_response_aggregation_policy_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [POLICY, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [POLICY, SUMMARY, DOC]):
        policy = pd.read_csv(POLICY)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        ids = set(policy["AggregationID"])
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING")
        add("family_clock_rules_present", {"AGG-01_PRIMARY_FAMILY", "AGG-02_PRIMARY_CLOCK"}.issubset(ids))
        add("rank_test_present", "AGG-03_RANK_TEST" in ids)
        add("dominance_cap_fixed", abs(float(summary["DominanceCap"]) - 0.5) < 1e-12)
        add("no_target_policy", not bool(policy["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(policy["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_report_only", "report-only" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_VALID" if ok else "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
