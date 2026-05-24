#!/usr/bin/env python3
"""Validate the P-TauCov parent-domain curvature source requirement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_v1"
STATUS = "P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_DEFINED_NO_OBJECT_NO_SCORING"

REQ = EVIDENCE / "p_taucov_parent_domain_curvature_source_requirement.csv"
SUMMARY = EVIDENCE / "p_taucov_parent_domain_curvature_source_requirement_summary.csv"
DOC = DOCS / "p_taucov_parent_domain_curvature_source_requirement.md"
OUT = EVIDENCE / "p_taucov_parent_domain_curvature_source_requirement_validation.csv"


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

    for path in [REQ, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if REQ.exists() and SUMMARY.exists() and DOC.exists():
        req = pd.read_csv(REQ)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_expected", str(summary["Status"]) == STATUS)
        add("requirement_count_matches", int(summary["Requirements"]) == len(req) == 8)
        add("object_not_constructed", not bool(summary["ObjectConstructed"]))
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("target_blindness_requirement_present", "PDCS-R8_TARGET_BLINDNESS" in set(req["RequirementID"]))
        add("forbidden_shortcut_documented", "Forbidden Shortcut" in doc and "K_tau := Q_clean K_arbitrary Q_clean" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_VALID" if ok else "P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
