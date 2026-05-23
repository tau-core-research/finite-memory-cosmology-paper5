#!/usr/bin/env python3
"""Validate readiness packet for the P3 balanced P-TauCov object."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_p3_balanced_readiness.csv"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_readiness_summary.csv"
DOC = ROOT / "docs/p_taucov_p3_balanced_readiness.md"
OUT = ROOT / "evidence/p_taucov_p3_balanced_readiness_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_READINESS_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_P3_BALANCED_READY_FOR_MANIFEST_NO_SCORING"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": True,
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    for path in [TABLE, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_READINESS_INVALID")
        return 1

    table = pd.read_csv(TABLE)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_ready", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "all_checks_pass", bool(table["Passed"].astype(bool).all()))
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "candidate_not_constructed", bool(summary["CandidateConstructed"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
    add(rows, "doc_mentions_no_scoring", "does not authorize scoring" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_READINESS_VALID" if ok else "P_TAUCOV_P3_BALANCED_READINESS_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
