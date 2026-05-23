#!/usr/bin/env python3
"""Validate the P-TauCov projection/morphology coupling gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_projection_morphology_coupling_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_morphology_coupling_gate_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_morphology_coupling_gate.md"
OUT = ROOT / "evidence/p_taucov_projection_morphology_coupling_gate_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_VALIDATION"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        gates = set(table["GateID"].astype(str))

        add("status_ready_no_object_no_scoring", str(summary["Status"]) == "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_READY_NO_OBJECT_NO_SCORING")
        add("all_gates_pass", bool(table["Passed"].all()))
        add("requires_d_p_mproj", "PMC-G6_NEXT_CANDIDATE_MUST_INCLUDE_D_P_MPROJ" in gates)
        add("requires_nondiagonal", "PMC-G7_NEXT_CANDIDATE_MUST_BE_NONDIAGONAL" in gates)
        add("requires_noncommuting_pmorph", "PMC-G8_NEXT_CANDIDATE_MUST_BE_NONCOMMUTING_WITH_PMORPH" in gates)
        add("no_score_or_target_gate", "PMC-G9_NO_SCORE_OR_TARGET_ACCESS" in gates)
        add("object_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(table["UsesScoreOutcome"].any()))
        add("doc_links_prior_preflight", "p_taucov_reduced_jacobian_specificity_preflight.md" in doc)
        add("doc_states_no_object_construction", "constructs a new" in doc and "authorizes scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_VALID" if ok else "P_TAUCOV_PROJECTION_MORPHOLOGY_COUPLING_GATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
