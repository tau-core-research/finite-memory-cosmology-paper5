#!/usr/bin/env python3
"""Validate the P-TauCov response/energy split packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ENERGY = ROOT / "evidence/p_taucov_response_energy_split_energy_hessian.csv"
RESPONSE = ROOT / "evidence/p_taucov_response_energy_split_effective_response.csv"
GATES = ROOT / "evidence/p_taucov_response_energy_split_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_response_energy_split_summary.csv"
DOC = ROOT / "docs/p_taucov_response_energy_split_packet.md"
OUT = ROOT / "evidence/p_taucov_response_energy_split_validation.csv"

AUDIT_ID = "P_TAUCOV_RESPONSE_ENERGY_SPLIT_VALIDATION"


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

    for path in [ENERGY, RESPONSE, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [ENERGY, RESPONSE, GATES, SUMMARY, DOC]):
        energy = pd.read_csv(ENERGY)
        response = pd.read_csv(RESPONSE)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_RESPONSE_ENERGY_SPLIT_PASS_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("positive_energy", float(summary["MinEnergyEigenvalue"]) > 0.0)
        add("signed_response", float(summary["MinEffectiveResponseEigenvalue"]) < 0.0)
        add("zero_response_mode_present", abs(float(summary["MaxEffectiveResponseEigenvalue"])) < 1e-12)
        add("response_not_energy_interpretation", str(summary["Interpretation"]) == "active_witness_is_response_operator_not_energy_hessian")
        add("still_open_expected", str(summary["StillOpen"]) == "COVARIANCE_MAP;FULL_DYNAMICAL_STABILITY")
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("uses_no_target_residuals", not bool(energy["UsesTargetResiduals"].any()) and not bool(response["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(energy["UsesScoreOutcome"].any()) and not bool(response["UsesScoreOutcome"].any()))
        add("doc_has_forbidden_boundary", "not a full dynamical stability theorem" in doc and "not measurement validation" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_RESPONSE_ENERGY_SPLIT_VALID" if ok else "P_TAUCOV_RESPONSE_ENERGY_SPLIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
