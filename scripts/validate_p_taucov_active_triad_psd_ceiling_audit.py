#!/usr/bin/env python3
"""Validate the active-triad PSD ceiling audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_active_triad_psd_ceiling_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_active_triad_psd_ceiling_audit_summary.csv"
DOC = ROOT / "docs/p_taucov_active_triad_psd_ceiling_audit.md"
OUT = ROOT / "evidence/p_taucov_active_triad_psd_ceiling_audit_validation.csv"

AUDIT_ID = "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_AUDIT_VALIDATION"


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

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")

        add("status_blocks_scoring", str(summary["Status"]) == "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_BLOCKS_SCORING_NO_SCORING")
        add("active_triad_available", bool(summary["ActiveTriadAvailable"]))
        add("scan_has_rows", int(summary["ScanRows"]) > 0)
        add("no_joint_pass_rows", int(summary["JointPassRows_DiagLe080_RankGe030"]) == 0)
        add("best_diag_above_threshold", float(summary["BestDiagonalEnergyShare"]) > 0.80)
        add("best_rank_below_threshold", float(summary["BestRankEffectiveRankFraction"]) < 0.30)
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(table["UsesScoreOutcome"].any()))
        add("doc_states_structural_ceiling", "structural ceiling" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_AUDIT_VALID" if ok else "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_AUDIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
