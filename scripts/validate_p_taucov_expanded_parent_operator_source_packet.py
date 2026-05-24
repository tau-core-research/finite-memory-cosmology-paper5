#!/usr/bin/env python3
"""Validate the expanded parent-operator source packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_expanded_parent_operator_source_matrix.csv"
GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_source_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_source_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_source_packet.md"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_source_validation.csv"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_PACKET_VALIDATION"


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

    for path in [MATRIX, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MATRIX, GATES, SUMMARY, DOC]):
        matrix = pd.read_csv(MATRIX)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        coords = set(matrix["RowCoordinate"].astype(str)) | set(matrix["ColumnCoordinate"].astype(str))

        add("status_ready_no_scoring", str(summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_READY_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("active_support_ge_5", int(summary["ActiveCoordinateSupportCount"]) >= 5)
        add("scale_axis_touched", "TEMPLATE_COORD_SCALE_UNIT" in coords)
        add("context_axis_touched", "TEMPLATE_EXT_OBSERVING_CONTEXT" in coords)
        add("source_family_not_touched", "TEMPLATE_EXT_SOURCE_FAMILY" not in coords)
        add("parent_morphology_not_touched", "TEMPLATE_M_PARENT_MORPHOLOGY" not in coords)
        add("forbidden_leakage_zero", float(summary["ForbiddenLeakageNorm"]) < 1e-12)
        add("object_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(matrix["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(matrix["UsesScoreOutcome"].any()))
        add("doc_states_no_covariance_object", "does not construct a covariance" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_PACKET_VALID" if ok else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_PACKET_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
