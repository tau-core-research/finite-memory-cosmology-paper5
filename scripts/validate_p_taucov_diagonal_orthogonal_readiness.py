#!/usr/bin/env python3
"""Validate readiness packet for diagonal-orthogonal P-TauCov candidate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_diagonal_orthogonal_readiness.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_readiness_summary.csv"
DOC = ROOT / "docs/p_taucov_diagonal_orthogonal_readiness.md"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_readiness_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_DIAGONAL_ORTHOGONAL_READINESS_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_ready", str(summary["Status"]) == "P_TAUCOV_DIAGONAL_ORTHOGONAL_READY_FOR_MANIFEST_NO_SCORING")
        add("all_checks_pass", bool(table["Passed"].all()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_manifest_required", "final manifest" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_DIAGONAL_ORTHOGONAL_READINESS_VALID" if ok else "P_TAUCOV_DIAGONAL_ORTHOGONAL_READINESS_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
