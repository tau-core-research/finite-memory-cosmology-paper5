#!/usr/bin/env python3
"""Validate branch-localized support rule for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / "evidence/p_taucov_branch_localized_support_rule.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_support_rule_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_support_rule.md"
OUT = ROOT / "evidence/p_taucov_branch_localized_support_rule_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [SUPPORT, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [SUPPORT, SUMMARY, DOC]):
        support = pd.read_csv(SUPPORT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_FROZEN_NO_SCORING")
        add("has_support_rows", int(summary["SupportRows"]) > 0)
        add("support_mass_positive", float(summary["SupportMass"]) > 0.0)
        add("threshold_fixed", abs(float(summary["Threshold"]) - 0.8) < 1e-12)
        add("no_target_residuals", not bool(support["UsesTargetResiduals"].any()))
        add("no_score_outcomes", not bool(support["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_target_blind", "target-blind" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_VALID" if ok else "P_TAUCOV_BRANCH_LOCALIZED_SUPPORT_RULE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
