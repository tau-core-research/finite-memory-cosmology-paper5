#!/usr/bin/env python3
"""Validate branch-localized covariance map for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "evidence/p_taucov_branch_localized_map.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_map_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_map.md"
OUT = ROOT / "evidence/p_taucov_branch_localized_map_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_BRANCH_LOCALIZED_MAP_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [MAP, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [MAP, SUMMARY, DOC]):
        mat = pd.read_csv(MAP)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen", str(summary["Status"]).startswith("P_TAUCOV_BRANCH_LOCALIZED_MAP_FROZEN_"))
        add("normalized", abs(float(summary["FrobeniusNorm"]) - 1.0) < 1e-12)
        add("dimension_positive", int(summary["MapDimension"]) > 0)
        add("no_target_residuals", not bool(mat["UsesTargetResiduals"].any()))
        add("no_score_outcomes", not bool(mat["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_signed_if_not_psd", "signed-response" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_BRANCH_LOCALIZED_MAP_VALID" if ok else "P_TAUCOV_BRANCH_LOCALIZED_MAP_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
