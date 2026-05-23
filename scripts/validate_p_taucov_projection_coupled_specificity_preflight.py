#!/usr/bin/env python3
"""Validate projection-coupled specificity preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "evidence/p_taucov_projection_coupled_specificity_preflight.csv"
SUMMARY = ROOT / "evidence/p_taucov_projection_coupled_specificity_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_coupled_specificity_preflight.md"
OUT = ROOT / "evidence/p_taucov_projection_coupled_specificity_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [PREFLIGHT, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [PREFLIGHT, SUMMARY, DOC]):
        preflight = pd.read_csv(PREFLIGHT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        failed = set(str(summary["FailedGates"]).split(";")) if str(summary["FailedGates"]) else set()

        add("status_fail_no_scoring", str(summary["Status"]) == "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_FAIL_NO_SCORING")
        add("some_gates_fail", int(summary["GatesPassed"]) < int(summary["GatesTotal"]))
        add("projection_channel_present_passed", bool(preflight.loc[preflight["GateID"].eq("PCS-G7_PROJECTION_CHANNEL_PRESENT"), "Passed"].iloc[0]))
        add("branch_channel_present_passed", bool(preflight.loc[preflight["GateID"].eq("PCS-G8_BRANCH_CHANNEL_PRESENT"), "Passed"].iloc[0]))
        add("diagonal_gate_failed", "PCS-G3_NOT_DIAGONAL_DOMINATED" in failed)
        add("rank_gate_failed", "PCS-G5_EFFECTIVE_RANK_NOT_TOO_LOW" in failed)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("doc_states_fails_before_scoring", "fails specificity" in doc and "before scoring" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_VALID" if ok else "P_TAUCOV_PROJECTION_COUPLED_SPECIFICITY_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
