#!/usr/bin/env python3
"""Validate the P-TauCov parent-Hessian residue gate packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_parent_hessian_residue_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_hessian_residue_gate_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_hessian_residue_gate.md"
OUT = ROOT / "evidence/p_taucov_parent_hessian_residue_gate_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_DEFINED_NO_OBJECT_NO_SCORING"


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
        gate_ids = set(table["GateID"].astype(str))
        required = {
            "PHR-G1_PARENT_HESSIAN_RESIDUE_DECLARED",
            "PHR-G2_SMOOTH_PSD_EXCLUSION",
            "PHR-G3_PROJECTION_NULL_EXCLUSION",
            "PHR-G4_SPECTRAL_RESIDUE_LOCALITY",
            "PHR-G5_PARENT_ORIENTATION_ANCHOR",
            "PHR-G6_BALANCED_SUPPORT_RETENTION",
            "PHR-G7_NO_TARGET_OR_SCORE_INPUTS",
        }
        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("all_required_gates_present", required.issubset(gate_ids))
        add("all_gates_required_before_scoring", bool(table["RequiredBeforeScoring"].all()))
        add("no_gate_authorizes_scoring", not bool(table["ScoringAuthorizedByGate"].any()))
        add("summary_scoring_false", bool(summary["ScoringAuthorized"]) is False)
        add("summary_survival_false", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("summary_tau_validation_false", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("records_expanded_smooth_failure", bool(summary["ExpandedSmoothPSDFailureObserved"]) is True)
        add("records_projection_null_failure", bool(summary["CommutatorProjectionNullFailureObserved"]) is True)
        add("doc_names_forbidden_claim", "Forbidden Claim" in doc and "found a Tau Core signal" in doc)
        add("doc_names_next_artifact", "p_taucov_parent_hessian_residue_candidate_v1_no_score_preflight" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_VALID" if ok else "P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
