#!/usr/bin/env python3
"""Validate the P-TauCov next-candidate admissibility gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate_summary.csv"
DOC = ROOT / "docs/p_taucov_next_candidate_admissibility_gate.md"
OUT = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        reqs = set(table["RequirementID"])
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_PASS_NO_SCORING")
        add("all_meta_gates_pass", bool(table["SatisfiedAsMetaGate"].all()))
        add("diagonal_gate_present", "NC-G2_DIAGONAL_ORTHOGONALITY_REQUIRED" in reqs)
        add("family_gate_present", "NC-G3_FAMILY_BALANCE_REQUIRED" in reqs)
        add("no_v4_search_present", "NC-G6_NO_V4_SCORE_SEARCH" in reqs)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(table["UsesScoreOutcome"].any()))
        add("doc_mentions_meta_gate", "meta-gate only" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_VALID" if ok else "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
