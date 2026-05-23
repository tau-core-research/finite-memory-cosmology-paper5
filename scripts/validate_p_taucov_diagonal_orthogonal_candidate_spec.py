#!/usr/bin/env python3
"""Validate diagonal-orthogonal signed-response candidate spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_summary.csv"
DOC = ROOT / "docs/p_taucov_diagonal_orthogonal_candidate_spec.md"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [MATRIX, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [MATRIX, SUMMARY, DOC]):
        matrix = pd.read_csv(MATRIX)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_SPEC_PASS_NO_SCORING")
        add("diagonal_zero", float(summary["FinalDiagonalNorm"]) < 1e-12)
        add("normalized", abs(float(summary["FrobeniusNorm"]) - 1.0) < 1e-12)
        add("no_target_residuals", not bool(matrix["UsesTargetResiduals"].any()))
        add("no_score_outcomes", not bool(matrix["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_no_scoring", "does not authorize scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_VALID" if ok else "P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
