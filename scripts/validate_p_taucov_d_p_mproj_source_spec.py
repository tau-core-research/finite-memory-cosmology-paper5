#!/usr/bin/env python3
"""Validate the P-TauCov D_P M_proj source spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence/p_taucov_d_p_mproj_source_spec_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_d_p_mproj_source_spec_summary.csv"
MATRIX = ROOT / "evidence/p_taucov_d_p_mproj_source_spec_matrix.csv"
DOC = ROOT / "docs/p_taucov_d_p_mproj_source_spec.md"
OUT = ROOT / "evidence/p_taucov_d_p_mproj_source_spec_validation.csv"

AUDIT_ID = "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_VALIDATION"


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

    for path in [AUDIT, SUMMARY, MATRIX, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [AUDIT, SUMMARY, MATRIX, DOC]):
        audit = pd.read_csv(AUDIT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        matrix = pd.read_csv(MATRIX)
        doc = DOC.read_text(encoding="utf-8")
        gates = set(audit["GateID"].astype(str))
        coords = set(matrix["RowCoordinate"].astype(str)) | set(matrix["ColumnCoordinate"].astype(str))

        add("status_frozen_no_object_no_scoring", str(summary["Status"]) == "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_FROZEN_NO_OBJECT_NO_SCORING")
        add("all_gates_pass", bool(audit["Passed"].all()))
        add("requires_no_forbidden_leakage", "DPM-G4_NO_FORBIDDEN_M_PARENT_LEAKAGE" in gates)
        add("requires_noncommuting_pmorph", "DPM-G6_NONCOMMUTING_WITH_ACTIVE_PMORPH" in gates)
        add("has_branch_coordinate", "TEMPLATE_B_BRANCH_RESPONSE" in coords)
        add("has_projection_coordinate", "TEMPLATE_P_MORPH_PROJECTION" in coords)
        add("no_parent_morphology_coordinate", "TEMPLATE_M_PARENT_MORPHOLOGY" not in coords)
        add("diagonal_share_zero", float(summary["DiagonalEnergyShare"]) == 0.0)
        add("commutator_share_nonzero", float(summary["ActiveProjectionCommutatorShare"]) >= 0.5)
        add("object_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(audit["UsesTargetResiduals"].any()) and not bool(matrix["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(audit["UsesScoreOutcome"].any()) and not bool(matrix["UsesScoreOutcome"].any()))
        add("doc_states_not_candidate", "not a new `delta_C_Tau` candidate" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_VALID" if ok else "P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
