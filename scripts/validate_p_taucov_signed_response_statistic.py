#!/usr/bin/env python3
"""Validate signed-response statistic definition for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_signed_response_statistic.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_statistic.md"
OUT = ROOT / "evidence/p_taucov_signed_response_statistic_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING")
        add("statistic_declared", str(summary["Statistic"]) == "trace((rrT/sigma2-I)K_signed)")
        add("no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("no_score_outcomes", not bool(table["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_says_not_likelihood", "not a covariance" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_SIGNED_RESPONSE_STATISTIC_VALID" if ok else "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
