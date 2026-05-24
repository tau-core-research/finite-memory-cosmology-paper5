#!/usr/bin/env python3
"""Validate the P-TauCov domain-metric candidate audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_v1"
EXPECTED_STATUS = "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_NO_PASSING_METRIC_NO_SCORING"

FILES = {
    "candidates": EVIDENCE / "p_taucov_domain_metric_candidate_audit.csv",
    "summary": EVIDENCE / "p_taucov_domain_metric_candidate_audit_summary.csv",
    "doc": DOCS / "p_taucov_domain_metric_candidate_audit.md",
}
OUT = EVIDENCE / "p_taucov_domain_metric_candidate_audit_validation.csv"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "FreezeID": FREEZE_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for key, path in FILES.items():
        add(f"exists_{key}", path.exists())
    if all(path.exists() for path in FILES.values()):
        candidates = pd.read_csv(FILES["candidates"])
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("five_candidates", len(candidates) == 5)
        add("no_passing_candidates", int(summary["PassingMetricCandidates"]) == 0)
        add("best_below_support_threshold", float(summary["BestMinActiveBranchQCleanSupport"]) < float(summary["SupportThreshold"]))
        add("metric_freeze_not_authorized", not bool(summary["MetricFreezeAuthorized"]))
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("doc_forbids_scoring", "empirical scoring is authorized" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_VALID" if ok else "P_TAUCOV_DOMAIN_METRIC_CANDIDATE_AUDIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
