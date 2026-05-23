#!/usr/bin/env python3
"""Validate the full-action domain/null-gauge packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COORDS = ROOT / "evidence/p_taucov_full_action_domain_coordinates.csv"
PROJECTORS = ROOT / "evidence/p_taucov_full_action_domain_projectors.csv"
GATES = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_summary.csv"
DOC = ROOT / "docs/p_taucov_full_action_domain_null_gauge_packet_result.md"
OUT = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_validation.csv"

AUDIT_ID = "P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [COORDS, PROJECTORS, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [COORDS, PROJECTORS, GATES, SUMMARY, DOC]):
        coords = pd.read_csv(COORDS)
        projectors = pd.read_csv(PROJECTORS)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        active = set(coords.loc[coords["EmbeddingRole"].eq("active"), "CoordinateID"])
        gauge = set(coords.loc[coords["EmbeddingRole"].eq("gauge"), "CoordinateID"])
        forbidden = set(coords.loc[coords["EmbeddingRole"].eq("forbidden"), "CoordinateID"])
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("eight_coordinates", int(summary["CoordinateCount"]) == 8 and len(coords) == 8)
        add("active_phi_b_p", active == {"TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE", "TEMPLATE_P_MORPH_PROJECTION"})
        add("gauge_convention_modes", gauge == {"TEMPLATE_COORD_ORIGIN_CENTER", "TEMPLATE_COORD_SCALE_UNIT"})
        add("forbidden_morphology_external", forbidden == {"TEMPLATE_M_PARENT_MORPHOLOGY", "TEMPLATE_EXT_SOURCE_FAMILY", "TEMPLATE_EXT_OBSERVING_CONTEXT"})
        add("projectors_present", {"P_active_reduced", "P_null", "P_gauge", "P_forbidden"}.issubset(set(projectors["ProjectorID"])))
        add("resolved_expected_blockers", str(summary["ResolvedBlockers"]) == "PARENT_DOMAIN;NULL_GAUGE_MODES")
        add("remaining_expected_blockers", str(summary["RemainingBlockers"]) == "REFERENCE_BACKGROUND;S_REST;COVARIANCE_MAP")
        add("scoring_not_authorized", not bool(coords["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_projection_active", "active reduced domain `Phi,B,P`" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_VALID" if ok else "P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
