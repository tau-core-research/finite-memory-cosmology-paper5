#!/usr/bin/env python3
"""Validate the P4 Tau-specific candidate preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "evidence/p_taucov_p4_tau_specific_candidate.csv"
GATES = ROOT / "evidence/p_taucov_p4_tau_specific_candidate_preflight_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_p4_tau_specific_candidate_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_p4_tau_specific_candidate_preflight.md"
OUT = ROOT / "evidence/p_taucov_p4_tau_specific_candidate_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_P4_TAU_SPECIFIC_CANDIDATE_PREFLIGHT_VALIDATION"


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

    for path in [CANDIDATE, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if CANDIDATE.exists() and GATES.exists() and SUMMARY.exists() and DOC.exists():
        candidate = pd.read_csv(CANDIDATE)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_fail_no_scoring", str(summary["Status"]).endswith("FAIL_NO_SCORING"))
        add("scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
        add("scoring_not_authorized_candidate", not bool(candidate["ScoringAuthorized"].any()))
        add("uses_no_target_residuals", not bool(candidate["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(candidate["UsesScoreOutcome"].any()))
        add("has_failed_gate", int((~gates["Passed"]).sum()) > 0)
        add("gates_match_summary", int(gates["Passed"].sum()) == int(summary["GatesPassed"]))
        add("doc_contains_no_survival_claim", "does not authorize" in doc and "survival claim" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_P4_TAU_SPECIFIC_PREFLIGHT_VALID" if ok else "P_TAUCOV_P4_TAU_SPECIFIC_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
