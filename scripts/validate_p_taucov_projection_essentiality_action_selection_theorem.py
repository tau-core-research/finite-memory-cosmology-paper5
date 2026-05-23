#!/usr/bin/env python3
"""Validate the projection-essentiality action-selection theorem packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CONSTRAINTS = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_constraints.csv"
COEFFS = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_coefficients.csv"
GATES = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_action_selection_packet.md"
OUT = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_VALIDATION"


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

    for path in [CONSTRAINTS, COEFFS, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [CONSTRAINTS, COEFFS, GATES, SUMMARY, DOC]):
        constraints = pd.read_csv(CONSTRAINTS)
        coeffs = pd.read_csv(COEFFS)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        lookup = coeffs.set_index("CoefficientID")["Value"]
        add("status_pass_no_scoring", str(summary["Status"]).endswith("PASS_NO_SCORING"))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("seven_constraints_declared", len(constraints) == 7)
        add("selected_pb_minus_two", abs(float(lookup["PB"]) + 2.0) < 1e-12)
        add("selected_pphi_minus_one", abs(float(lookup["P_PHI"]) + 1.0) < 1e-12)
        add("selected_b2_minus_half", abs(float(lookup["B2"]) + 0.5) < 1e-12)
        add("self_energies_zero", abs(float(lookup["P2"])) < 1e-12 and abs(float(lookup["PHI2"])) < 1e-12)
        add("branch_response_minus_two", abs(float(summary["BranchResponseBStarOverP"]) + 2.0) < 1e-12)
        add("uses_no_target_residuals", not bool(constraints["UsesTargetResiduals"].any()) and not bool(coeffs["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(constraints["UsesScoreOutcome"].any()) and not bool(coeffs["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(coeffs["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("doc_contains_uniqueness_boundary", "uniqueness under the declared local constraints" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_VALID" if ok else "P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
