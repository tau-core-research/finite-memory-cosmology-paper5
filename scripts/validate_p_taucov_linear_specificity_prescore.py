#!/usr/bin/env python3
"""Validate the P-TauCov linear specificity prescore output."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_specificity_prescore.md"
CSV = ROOT / "evidence/p_taucov_linear_specificity_prescore.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_specificity_prescore_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_specificity_prescore_validation.csv"


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("prescore_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("status_blocked", summary["Status"].iloc[0] == "BLOCKED")
    add(
        "blocked_for_missing_model_packet",
        summary["BlockReason"].iloc[0] == "missing_target_blind_linear_model_packet",
    )
    add("metrics_not_evaluated", not bool(summary["MetricsEvaluated"].iloc[0]))
    add("linear_not_frozen", not bool(summary["LinearCandidateFrozen"].iloc[0]))
    add("delta_c_tau_not_generated", not bool(summary["DeltaCTauGenerated"].iloc[0]))
    add("scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("all_rows_blocked", set(df["Status"]) == {"BLOCKED"})
    add("no_target_residuals", not df["UsesTargetResiduals"].astype(bool).any())
    add("no_p5c_v3_outcome", not df["UsesP5Cv3Outcome"].astype(bool).any())
    for phrase in [
        "missing_target_blind_linear_model_packet",
        "evidence/p_taucov_linear_model_packet.yaml",
        "L0_B",
        "The strictly linear candidate passed the specificity audit",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_VALID_BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
