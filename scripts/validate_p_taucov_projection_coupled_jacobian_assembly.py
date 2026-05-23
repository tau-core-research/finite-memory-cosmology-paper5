#!/usr/bin/env python3
"""Validate the projection-coupled reduced-Jacobian assembly."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "evidence/p_taucov_projection_coupled_jacobian_assembly_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_coupled_jacobian_assembly_summary.csv"
MATRIX = ROOT / "evidence/p_taucov_projection_coupled_jacobian_assembly_matrix.csv"
COV = ROOT / "evidence/p_taucov_projection_coupled_delta_c_tau_candidate.csv"
DOC = ROOT / "docs/p_taucov_projection_coupled_jacobian_assembly.md"
OUT = ROOT / "evidence/p_taucov_projection_coupled_jacobian_assembly_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_VALIDATION"


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

    for path in [GATES, SUMMARY, MATRIX, COV, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [GATES, SUMMARY, MATRIX, COV, DOC]):
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        matrix = pd.read_csv(MATRIX)
        doc = DOC.read_text(encoding="utf-8")
        coords = set(matrix["RowCoordinate"].astype(str)) | set(matrix["ColumnCoordinate"].astype(str))

        add("status_assembled_no_scoring", str(summary["Status"]) == "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLED_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("projection_derivative_included", bool(summary["ProjectionDerivativeIncluded"]))
        add("has_projection_coordinate", "TEMPLATE_P_MORPH_PROJECTION" in coords)
        add("has_branch_coordinate", "TEMPLATE_B_BRANCH_RESPONSE" in coords)
        add("no_forbidden_leakage", float(summary["ForbiddenGaugeLeakageNorm"]) < 1e-12)
        add("commutator_present", float(summary["ActiveProjectionCommutatorShare"]) > 0.0)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(gates.get("UsesTargetResiduals", pd.Series([False])).any()) and not bool(matrix["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(gates.get("UsesScoreOutcome", pd.Series([False])).any()) and not bool(matrix["UsesScoreOutcome"].any()))
        add("doc_states_no_scoring", "no-scoring assembly step" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_VALID" if ok else "P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
