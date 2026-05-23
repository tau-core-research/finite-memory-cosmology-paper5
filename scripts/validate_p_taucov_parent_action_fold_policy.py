#!/usr/bin/env python3
"""Validate the parent-action P-TauCov fold policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_parent_action_fold_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_fold_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_fold_policy.md"
OUT = ROOT / "evidence/p_taucov_parent_action_fold_policy_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [POLICY, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [POLICY, SUMMARY, DOC]):
        policy = pd.read_csv(POLICY)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        primary_ids = set(policy.loc[policy["Primary"], "FoldPolicyID"])
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FROZEN_NO_SCORING")
        add("primary_family_and_clock", {"PRIMARY_LOFO_FAMILY", "PRIMARY_CLOCK_BLOCK"}.issubset(primary_ids))
        add("diagnostics_not_primary", not bool(policy.loc[policy["FoldPolicyID"].isin(["SECONDARY_FAMILY_X_CLOCK", "STRESS_OUTSIDE_BRANCH"]), "Primary"].any()))
        add("no_target_policy", not bool(policy["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(policy["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["PTauCovScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_no_target", "No target residuals" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_FOLD_POLICY_VALID" if ok else "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
