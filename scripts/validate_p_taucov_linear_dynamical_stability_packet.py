#!/usr/bin/env python3
"""Validate the P-TauCov linear dynamical stability packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODES = ROOT / "evidence/p_taucov_linear_dynamical_stability_modes.csv"
GATES = ROOT / "evidence/p_taucov_linear_dynamical_stability_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_dynamical_stability_summary.csv"
DOC = ROOT / "docs/p_taucov_linear_dynamical_stability_packet.md"
OUT = ROOT / "evidence/p_taucov_linear_dynamical_stability_validation.csv"

AUDIT_ID = "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_VALIDATION"


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

    for path in [MODES, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [MODES, GATES, SUMMARY, DOC]):
        modes = pd.read_csv(MODES)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_PASS_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("bounded_modes", bool(summary["BoundedLinearModes"]) is True)
        add("positive_kinetic", float(summary["MinKineticEigenvalue"]) > 0.0)
        add("positive_stiffness", float(summary["MinStiffnessEigenvalue"]) > 0.0)
        add("static_response_preserved", bool(summary["StaticResponsePreserved"]) is True)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(modes["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(modes["UsesScoreOutcome"].any()))
        add("doc_mentions_uv_not_complete", "not a UV completion" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_VALID" if ok else "P_TAUCOV_LINEAR_DYNAMICAL_STABILITY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
