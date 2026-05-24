#!/usr/bin/env python3
"""Validate the P-TauCov parent-operator source expansion gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_parent_operator_source_expansion_gate.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_operator_source_expansion_gate_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_operator_source_expansion_gate.md"
OUT = ROOT / "evidence/p_taucov_parent_operator_source_expansion_gate_validation.csv"

AUDIT_ID = "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_VALIDATION"


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
        allowed = set(str(summary["AllowedSourceClasses"]).split(";"))
        forbidden = set(str(summary["ForbiddenSourceClasses"]).split(";"))

        add("status_ready_no_object_no_scoring", str(summary["Status"]) == "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_READY_NO_OBJECT_NO_SCORING")
        add("all_gates_pass", bool(table["Passed"].all()))
        add("ceiling_gate_present", "POSE-G1_ACTIVE_TRIAD_CEILING_CONFIRMED" in gates)
        add("minimum_active_coord_gate_present", "POSE-G5_MINIMUM_ACTIVE_COORDINATES_GE_5" in gates)
        add("new_nonoutcome_axes_gate_present", "POSE-G6_AT_LEAST_TWO_NEW_NONOUTCOME_AXES" in gates)
        add("operator_before_matrix_gate_present", "POSE-G7_OPERATOR_SOURCE_BEFORE_MATRIX" in gates)
        add("allowed_tau_side_symbolic", "TauSideSymbolicDefinition" in allowed)
        add("allowed_published_metadata", "PublishedExternalMetadata" in allowed)
        add("forbids_p5c_gains", "ExistingP5CKernelV3Gains" in forbidden)
        add("forbids_targets", "HeldOutResidualsOrTargets" in forbidden)
        add("object_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(table["UsesScoreOutcome"].any()))
        add("doc_states_not_constructing_object", "constructs an expanded object" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_VALID" if ok else "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
