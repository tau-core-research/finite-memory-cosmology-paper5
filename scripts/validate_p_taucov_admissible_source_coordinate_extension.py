#!/usr/bin/env python3
"""Validate the P-TauCov admissible source-coordinate extension packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_v1"
ALLOWED_STATUSES = {
    "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_HAS_PREFLIGHT_COORDINATE_NO_SCORING",
    "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_NO_PASSING_COORDINATE_NO_SCORING",
}

FILES = {
    "rule": EVIDENCE / "p_taucov_admissible_source_coordinate_extension_rule.csv",
    "audit": EVIDENCE / "p_taucov_admissible_source_coordinate_extension_audit.csv",
    "summary": EVIDENCE / "p_taucov_admissible_source_coordinate_extension_summary.csv",
    "doc": DOCS / "p_taucov_admissible_source_coordinate_extension.md",
}
OUT = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_validation.csv"


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
        rule = pd.read_csv(FILES["rule"])
        audit = pd.read_csv(FILES["audit"])
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_allowed", str(summary["Status"]) in ALLOWED_STATUSES)
        add("rule_has_eight_rows", len(rule) == 8)
        add("audit_has_five_candidates", len(audit) == 5)
        add("no_scoring_authorized_rule", not bool(rule["ScoringAuthorized"].any()))
        add("no_scoring_authorized_audit", not bool(audit["ScoringAuthorized"].any()))
        add("summary_no_scoring", not bool(summary["ScoringAuthorized"]))
        add("summary_no_survival_claim", not bool(summary["SurvivalClaimAuthorized"]))
        add("summary_no_tau_validation", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("best_matches_audit", str(summary["BestCandidateID"]) == str(audit.iloc[0]["CoordinateCandidateID"]))
        add("doc_links_precursors", "p_taucov_domain_metric_candidate_audit.md" in doc)
        add("doc_forbids_validation_claim", "Tau Core is validated" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_VALID" if ok else "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
