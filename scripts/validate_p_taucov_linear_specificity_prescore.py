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

    status = str(summary["Status"].iloc[0])
    metrics_evaluated = bool(summary["MetricsEvaluated"].iloc[0])
    add("status_valid", status in {"BLOCKED", "PASS_NOT_FROZEN", "FAIL_STRICT_LINEAR_REJECTED"})
    if status == "BLOCKED":
        add(
            "blocked_for_known_reason",
            str(summary["BlockReason"].iloc[0])
            in {
                "missing_target_blind_linear_model_packet",
                "missing_threshold_freeze",
                "missing_metric_registry",
                "model_packet_missing_input_files",
                "model_packet_leakage_flags_not_false",
                "model_packet_score_or_p5c_leakage_flags_not_false",
            },
        )
        add("metrics_not_evaluated_when_blocked", not metrics_evaluated)
        add("all_rows_blocked_when_blocked", set(df["Status"]) == {"BLOCKED"})
    else:
        add("metrics_evaluated_when_not_blocked", metrics_evaluated)
        add("strict_linear_rejected_or_pass_not_frozen", status in {"PASS_NOT_FROZEN", "FAIL_STRICT_LINEAR_REJECTED"})
        add("all_rows_pass_or_fail_when_evaluated", set(df["Status"]).issubset({"PASS", "FAIL"}))
        add("metric_count_six", len(df) == 6)
    add("linear_not_frozen", not bool(summary["LinearCandidateFrozen"].iloc[0]))
    add("scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("no_target_residuals", not df["UsesTargetResiduals"].astype(bool).any())
    add("no_p5c_v3_outcome", not df["UsesP5Cv3Outcome"].astype(bool).any())
    for phrase in [
        "P-TauCov Linear Specificity Prescore",
        "L0_B",
        "PTauCovScoringAuthorized: false",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_INVALID")
        print(failed.to_string(index=False))
        return 1

    if status == "FAIL_STRICT_LINEAR_REJECTED":
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_VALID_FAIL_STRICT_LINEAR_REJECTED")
    elif status == "PASS_NOT_FROZEN":
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_VALID_PASS_NOT_FROZEN")
    else:
        print("P_TAUCOV_LINEAR_SPECIFICITY_PRESCORE_VALID_BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
