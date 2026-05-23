#!/usr/bin/env python3
"""Validate the reduced-Jacobian assembly artifact."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
J_MATRIX = ROOT / "evidence/p_taucov_reduced_jacobian_assembly_matrix.csv"
DELTA_C = ROOT / "evidence/p_taucov_reduced_jacobian_delta_c_tau_candidate.csv"
GATES = ROOT / "evidence/p_taucov_reduced_jacobian_assembly_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_reduced_jacobian_assembly_summary.csv"
DOC = ROOT / "docs/p_taucov_reduced_jacobian_assembly.md"
OUT = ROOT / "evidence/p_taucov_reduced_jacobian_assembly_validation.csv"

AUDIT_ID = "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_VALIDATION"


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

    for path in [J_MATRIX, DELTA_C, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [J_MATRIX, DELTA_C, GATES, SUMMARY, DOC]):
        j_matrix = pd.read_csv(J_MATRIX)
        delta_c = pd.read_csv(DELTA_C)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_assembled_no_scoring", str(summary["Status"]) == "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLED_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("j_nonzero", float(summary["JResponseFrobeniusNorm"]) > 0.0 and len(j_matrix) > 0)
        add("delta_c_normalized", abs(float(summary["DeltaCTauFrobeniusNorm"]) - 1.0) < 1e-12)
        add("delta_c_psd", float(summary["DeltaCTauMinEigenvalue"]) >= -1e-12)
        add("strict_branch_only", str(summary["AssemblyMode"]) == "STRICT_BRANCH_ONLY")
        add("projection_derivative_not_included", bool(summary["ProjectionDerivativeIncluded"]) is False)
        add("full_coordinate_count", int(summary["CoordinateCount"]) == 8)
        add("reduced_coordinate_count", int(summary["ReducedCoordinateCount"]) == 3)
        add("forbidden_gauge_leakage_zero", abs(float(summary["ForbiddenGaugeLeakageNorm"])) < 1e-12)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_or_score", not bool(j_matrix["UsesTargetResiduals"].any()) and not bool(delta_c["UsesScoreOutcome"].any()))
        add("doc_forbids_scoring_and_validation", "authorizes scoring" in doc and "validates Tau" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_VALID" if ok else "P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
