#!/usr/bin/env python3
"""Validate parent-action P-TauCov null comparator policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_parent_action_null_comparators.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_null_comparators_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_null_comparators.md"
OUT = ROOT / "evidence/p_taucov_parent_action_null_comparators_validation.csv"

REQUIRED = {
    "OUTSIDE_BRANCH",
    "SHUFFLED_SUPPORT",
    "MORPHOLOGY_NULL",
    "PROJECTION_NULL",
    "GENERIC_RANDOM_SMOOTH_PSD",
    "GENERIC_FAMILY_PERMUTED",
    "GENERIC_DIAGONAL",
    "GENERIC_WRONG_CLOCK",
    "GENERIC_PHASE_SHIFT",
}


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [POLICY, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [POLICY, SUMMARY, DOC]):
        policy = pd.read_csv(POLICY)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        required_ids = set(policy.loc[policy["Required"], "NullID"])
        primary_defeat_ids = set(policy.loc[policy["PrimaryDefeatRequired"], "NullID"])
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FROZEN_NO_SCORING")
        add("required_ids_present", REQUIRED.issubset(required_ids))
        add("primary_defeat_required", REQUIRED.issubset(primary_defeat_ids))
        add("diagnostic_not_primary", "OSCILLATORY_DIAGNOSTIC" not in primary_defeat_ids)
        add("no_target_policy", not bool(policy["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(policy["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["PTauCovScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_projection_null", "projection null" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_VALID" if ok else "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
