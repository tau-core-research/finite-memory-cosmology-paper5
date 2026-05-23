#!/usr/bin/env python3
"""Validate family-balance policy for the next P-TauCov candidate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_family_balance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_family_balance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_family_balance_policy.md"
OUT = ROOT / "evidence/p_taucov_family_balance_policy_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_FAMILY_BALANCE_POLICY_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [POLICY, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [POLICY, SUMMARY, DOC]):
        policy = pd.read_csv(POLICY)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_FAMILY_BALANCE_POLICY_FROZEN_NO_SCORING")
        add("families_at_least_two", int(summary["Families"]) >= 2)
        add("min_positive_two", int(summary["MinPositiveFamiliesRequired"]) == 2)
        add("cap_half", abs(float(summary["MaxAllowedPositiveContributionShare"]) - 0.5) < 1e-12)
        add("lofo_primary_present", int(summary["PrimaryLOFOFolds"]) >= int(summary["Families"]))
        add("clock_primary_present", int(summary["PrimaryClockFolds"]) >= 1)
        add("no_target_policy", not bool(policy["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(policy["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_one_family", "one family" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_FAMILY_BALANCE_POLICY_VALID" if ok else "P_TAUCOV_FAMILY_BALANCE_POLICY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
