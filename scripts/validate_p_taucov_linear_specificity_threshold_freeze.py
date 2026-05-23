#!/usr/bin/env python3
"""Validate the P-TauCov linear specificity threshold freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_specificity_threshold_freeze.md"
CSV = ROOT / "evidence/p_taucov_linear_specificity_threshold_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_specificity_threshold_freeze_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_specificity_threshold_freeze_validation.csv"

REQUIRED_METRICS = {
    "M1_NONCOMMUTATOR_SHARE",
    "M2_EFFECTIVE_RANK",
    "M3_SUPPORT_ENTROPY",
    "M4_LABEL_PROXY_OVERLAP",
    "M5_NULL_SEPARATION_MARGIN",
    "M6_OUTCOME_LEAKAGE_CERTIFICATE",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SPECIFICITY_THRESHOLD_FREEZE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("threshold_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_SPECIFICITY_THRESHOLD_FREEZE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_metrics_present", REQUIRED_METRICS.issubset(set(df["MetricID"])))
    add("thresholds_frozen_before_evaluation", df["ThresholdFrozenBeforeEvaluation"].astype(bool).all())
    add("metrics_not_evaluated", not df["MetricEvaluated"].astype(bool).any())
    add("linear_not_frozen", not df["LinearCandidateFrozen"].astype(bool).any())
    add("no_scoring_authorized", not df["ScoringAuthorized"].astype(bool).any())
    add("summary_metrics_not_evaluated", not bool(summary["MetricsEvaluated"].iloc[0]))
    add("summary_delta_c_tau_not_generated", not bool(summary["DeltaCTauGenerated"].iloc[0]))
    add("summary_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    for phrase in [
        ">=0.10",
        "0.10 <= effective_rank_fraction <= 0.85",
        "0.25 <= normalized_entropy <= 0.85",
        "<=0.35",
        ">=0.05",
        "must_be_true",
        "The frozen thresholds show that the strictly linear candidate passes",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SPECIFICITY_THRESHOLD_FREEZE_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SPECIFICITY_THRESHOLD_FREEZE_VALID_NOT_EVALUATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
