#!/usr/bin/env python3
"""Validate the expanded parent-operator domain packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_coordinates.csv"
PROJECTORS = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_projectors.csv"
GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_domain_packet.md"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_domain_validation.csv"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_PACKET_VALIDATION"


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

    for path in [COORDS, PROJECTORS, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [COORDS, PROJECTORS, GATES, SUMMARY, DOC]):
        coords = pd.read_csv(COORDS)
        projectors = pd.read_csv(PROJECTORS)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")

        active = set(coords.loc[coords["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
        forbidden = set(coords.loc[coords["EmbeddingRole"].eq("forbidden"), "CoordinateID"].astype(str))
        new_active = set(coords.loc[coords["NewActiveAxis"].astype(bool), "CoordinateID"].astype(str))

        add("status_ready_no_object_no_scoring", str(summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_READY_NO_OBJECT_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("active_count_ge_5", int(summary["ActiveCount"]) >= 5)
        add("new_active_count_ge_2", int(summary["NewActiveNonOutcomeAxes"]) >= 2)
        add("scale_unit_new_active", "TEMPLATE_COORD_SCALE_UNIT" in new_active)
        add("observing_context_new_active", "TEMPLATE_EXT_OBSERVING_CONTEXT" in new_active)
        add("source_family_forbidden", "TEMPLATE_EXT_SOURCE_FAMILY" in forbidden)
        add("parent_morphology_forbidden", "TEMPLATE_M_PARENT_MORPHOLOGY" in forbidden)
        add("core_triad_still_active", {"TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE", "TEMPLATE_P_MORPH_PROJECTION"}.issubset(active))
        add("expanded_projector_present", bool(projectors["ProjectorID"].eq("P_expanded_active_reduced").any()))
        add("object_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(coords["UsesTargetResiduals"].any()) and not bool(projectors["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(coords["UsesScoreOutcome"].any()) and not bool(projectors["UsesScoreOutcome"].any()))
        add("doc_states_no_covariance_object", "constructs a covariance object" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_PACKET_VALID" if ok else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_PACKET_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
