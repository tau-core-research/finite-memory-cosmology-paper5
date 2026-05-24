#!/usr/bin/env python3
"""Validate the expanded parent-operator PSD preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COV = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_candidate.csv"
GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_preflight.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_psd_preflight.md"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_psd_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_VALIDATION"


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

    for path in [COV, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [COV, GATES, SUMMARY, DOC]):
        cov = pd.read_csv(COV)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")

        add("status_pass_no_scoring", str(summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_PASS_NO_SCORING")
        add("all_gates_pass", bool(gates["Passed"].all()))
        add("diagonal_below_threshold", float(summary["DiagonalEnergyShare"]) <= 0.80)
        add("effective_rank_above_threshold", float(summary["EffectiveRankFraction"]) >= 0.30)
        add("active_support_ge_5", int(summary["ActiveSupportCount"]) >= 5)
        add("forbidden_leakage_zero", float(summary["ForbiddenLeakageNorm"]) < 1e-12)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(cov["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(cov["UsesScoreOutcome"].any()))
        add("doc_states_no_scoring_authorization", "does not authorize empirical scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_VALID" if ok else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
