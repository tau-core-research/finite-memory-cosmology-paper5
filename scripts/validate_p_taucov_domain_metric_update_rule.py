#!/usr/bin/env python3
"""Validate the P-TauCov domain-metric update rule."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

RULE_ID = "P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_v1"
EXPECTED_STATUS = "P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_DEFINED_NO_METRIC_NO_SCORING"

RULES = EVIDENCE / "p_taucov_domain_metric_update_rule.csv"
SUMMARY = EVIDENCE / "p_taucov_domain_metric_update_rule_summary.csv"
DOC = DOCS / "p_taucov_domain_metric_update_rule.md"
OUT = EVIDENCE / "p_taucov_domain_metric_update_rule_validation.csv"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "RuleID": RULE_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [RULES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if RULES.exists() and SUMMARY.exists() and DOC.exists():
        rules = pd.read_csv(RULES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("rule_count", len(rules) == 7 and int(summary["Requirements"]) == 7)
        add("no_concrete_metric", not bool(summary["ConcreteMetricDefined"]))
        add("metric_eval_not_authorized", not bool(summary["MetricEvaluationAuthorized"]))
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("target_forbidden_rule_present", "DMR-R2_NO_TARGET_OUTCOME_INPUT" in set(rules["RequirementID"]))
        add("qclean_shortcut_forbidden", "DMR-R5_NO_QCLEAN_AS_SOURCE" in set(rules["RequirementID"]))
        add("doc_forbids_support_fitting", "choose G_domain" in doc and "not allowed" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_VALID" if ok else "P_TAUCOV_DOMAIN_METRIC_UPDATE_RULE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
