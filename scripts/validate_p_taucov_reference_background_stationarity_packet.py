#!/usr/bin/env python3
"""Validate the P-TauCov reference-background stationarity packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BACKGROUND = ROOT / "evidence/p_taucov_reference_background_stationarity.csv"
GATES = ROOT / "evidence/p_taucov_reference_background_stationarity_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_reference_background_stationarity_summary.csv"
DOC = ROOT / "docs/p_taucov_reference_background_stationarity_packet_result.md"
OUT = ROOT / "evidence/p_taucov_reference_background_stationarity_validation.csv"

AUDIT_ID = "P_TAUCOV_REFERENCE_BACKGROUND_STATIONARITY_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [BACKGROUND, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [BACKGROUND, GATES, SUMMARY, DOC]):
        background = pd.read_csv(BACKGROUND)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        refs = background[background["Role"].eq("active_reference_background")]
        grads = background[background["Role"].eq("active_gradient_at_reference")]
        add("status_stationary_stability_deferred", "STATIONARY_STABILITY_DEFERRED" in str(summary["Status"]))
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("reference_values_zero", bool((refs["ReferenceValue"].abs() < 1e-12).all()))
        add("gradient_values_zero", bool((grads["ReferenceValue"].abs() < 1e-12).all()))
        add("summary_stationary_true", bool(summary["ReferenceBackgroundStationary"]) is True)
        add("full_stability_not_claimed", bool(summary["FullStabilityProven"]) is False)
        add("remaining_blocker_s_rest", str(summary["RemainingBlocker"]) == "REFERENCE_BACKGROUND_STABILITY_REQUIRES_S_REST")
        add("scoring_not_authorized", not bool(background["ScoringAuthorized"].any()) and bool(summary["ScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_stability_deferred", "Full stability is not claimed" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_REFERENCE_BACKGROUND_STATIONARITY_VALID" if ok else "P_TAUCOV_REFERENCE_BACKGROUND_STATIONARITY_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
