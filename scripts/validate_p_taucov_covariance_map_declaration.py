#!/usr/bin/env python3
"""Validate the P-TauCov covariance map declaration."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "evidence/p_taucov_covariance_map_matrix.csv"
GATES = ROOT / "evidence/p_taucov_covariance_map_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_covariance_map_summary.csv"
DOC = ROOT / "docs/p_taucov_covariance_map_declaration.md"
OUT = ROOT / "evidence/p_taucov_covariance_map_validation.csv"

AUDIT_ID = "P_TAUCOV_COVARIANCE_MAP_DECLARATION_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [MAP, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MAP, GATES, SUMMARY, DOC]):
        matrix = pd.read_csv(MAP)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_COVARIANCE_MAP_DECLARED_PASS_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("map_psd", bool(summary["MapPositiveSemidefinite"]) is True)
        add("map_symmetric", bool(summary["MapSymmetric"]) is True)
        add("map_nonzero_normalized", abs(float(summary["FrobeniusNorm"]) - 1.0) < 1e-12)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(matrix["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(matrix["UsesScoreOutcome"].any()))
        add("doc_mentions_no_scorecard", "not a covariance scorecard" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_COVARIANCE_MAP_DECLARATION_VALID" if ok else "P_TAUCOV_COVARIANCE_MAP_DECLARATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
