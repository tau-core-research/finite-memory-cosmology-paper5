#!/usr/bin/env python3
"""Validate parent-action P-TauCov df/covariance policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "evidence/p_taucov_parent_action_df_covariance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_df_covariance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_df_covariance_policy.md"
OUT = ROOT / "evidence/p_taucov_parent_action_df_covariance_policy_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [POLICY, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [POLICY, SUMMARY, DOC]):
        policy = pd.read_csv(POLICY)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        ids = set(policy["PolicyID"])
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING")
        add("df_one", int(summary["DeclaredDF"]) == 1)
        add("psd_primary", str(summary["PrimaryKernelPolicy"]) == "PSD")
        add("required_policies_present", {"PARAM_ALPHA", "KERNEL_POLICY", "INFORMATION_CRITERION", "NO_SECONDARY_RESCUE"}.issubset(ids))
        add("no_target_policy", not bool(policy["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(policy["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["PTauCovScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_df1", "df=1" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_VALID" if ok else "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
