#!/usr/bin/env python3
"""Validate the P-TauCov S_rest no-leakage packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "evidence/p_taucov_s_rest_no_leakage_terms.csv"
HESSIAN = ROOT / "evidence/p_taucov_s_rest_no_leakage_hessian.csv"
GATES = ROOT / "evidence/p_taucov_s_rest_no_leakage_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_s_rest_no_leakage_summary.csv"
DOC = ROOT / "docs/p_taucov_s_rest_no_leakage_packet_result.md"
OUT = ROOT / "evidence/p_taucov_s_rest_no_leakage_validation.csv"

AUDIT_ID = "P_TAUCOV_S_REST_NO_LEAKAGE_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [TERMS, HESSIAN, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TERMS, HESSIAN, GATES, SUMMARY, DOC]):
        terms = pd.read_csv(TERMS)
        hessian = pd.read_csv(HESSIAN)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("inactive_positive", float(summary["MinInactiveEigenvalue"]) > 0.0)
        add("active_block_zero", float(summary["ActiveBlockNorm"]) < 1e-12)
        add("cross_block_zero", float(summary["ActiveInactiveCrossBlockNorm"]) < 1e-12)
        add("resolved_s_rest", str(summary["ResolvedBlocker"]) == "S_REST")
        add("remaining_expected", str(summary["StillOpen"]) == "REFERENCE_BACKGROUND_STABILITY;COVARIANCE_MAP")
        add("uses_no_target_residuals", not bool(terms["UsesTargetResiduals"].any()) and not bool(hessian["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(terms["UsesScoreOutcome"].any()) and not bool(hessian["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(terms["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_remaining_open", "REFERENCE_BACKGROUND_STABILITY" in doc and "COVARIANCE_MAP" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_S_REST_NO_LEAKAGE_VALID" if ok else "P_TAUCOV_S_REST_NO_LEAKAGE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
