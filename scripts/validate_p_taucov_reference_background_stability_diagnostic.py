#!/usr/bin/env python3
"""Validate the P-TauCov reference-background stability diagnostic."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EIGENVALUES = ROOT / "evidence/p_taucov_reference_background_stability_eigenvalues.csv"
GATES = ROOT / "evidence/p_taucov_reference_background_stability_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_reference_background_stability_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_background_stability_diagnostic.md"
OUT = ROOT / "evidence/p_taucov_reference_background_stability_validation.csv"

AUDIT_ID = "P_TAUCOV_REFERENCE_BACKGROUND_STABILITY_DIAGNOSTIC_VALIDATION"


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

    for path in [EIGENVALUES, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [EIGENVALUES, GATES, SUMMARY, DOC]):
        eigenvalues = pd.read_csv(EIGENVALUES)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_is_expected_saddle", str(summary["Status"]) == "P_TAUCOV_REFERENCE_BACKGROUND_ACTIVE_SADDLE_STABILITY_NOT_PROVEN_NO_SCORING")
        add("has_three_active_eigenvalues", len(eigenvalues) == 3)
        add("has_negative_mode", int(summary["NegativeEigenvalueCount"]) > 0)
        add("has_positive_mode", int(summary["PositiveEigenvalueCount"]) > 0)
        add("active_psd_false", bool(summary["ActiveHessianPositiveSemidefinite"]) is False)
        add("full_stability_not_proven", bool(summary["FullStabilityProven"]) is False)
        add("stationary_still_true", bool(summary["ReferenceBackgroundStationary"]) is True)
        add("s_rest_no_leakage_true", bool(summary["SRestNoLeakagePass"]) is True)
        add("remaining_blockers_expected", str(summary["RemainingBlockers"]) == "REFERENCE_BACKGROUND_STABILITY;COVARIANCE_MAP")
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("required_failure_kept_visible", not bool(gates.loc[gates["GateID"].eq("RBS-G4_ACTIVE_HESSIAN_POSITIVE_SEMIDEFINITE"), "Passed"].iloc[0]))
        add("doc_mentions_response_not_energy", "response operator" in doc and "energy Hessian" in doc)
        add("uses_no_target_residuals", not bool(eigenvalues["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(eigenvalues["UsesScoreOutcome"].any()))

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_REFERENCE_BACKGROUND_STABILITY_DIAGNOSTIC_VALID" if ok else "P_TAUCOV_REFERENCE_BACKGROUND_STABILITY_DIAGNOSTIC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
