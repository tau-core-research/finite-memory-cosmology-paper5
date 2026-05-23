#!/usr/bin/env python3
"""Validate the P-TauCov linear specificity metric registry."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_specificity_metric_registry.md"
CSV = ROOT / "evidence/p_taucov_linear_specificity_metric_registry.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_specificity_metric_registry_summary.csv"
OUT = ROOT / "evidence/p_taucov_linear_specificity_metric_registry_validation.csv"

REQUIRED_METRICS = {
    "M1_NONCOMMUTATOR_SHARE",
    "M2_EFFECTIVE_RANK",
    "M3_SUPPORT_ENTROPY",
    "M4_LABEL_PROXY_OVERLAP",
    "M5_NULL_SEPARATION_MARGIN",
    "M6_OUTCOME_LEAKAGE_CERTIFICATE",
}

REQUIRED_NULLS = {
    "SHUFFLED_BRANCH_OPERATOR",
    "COMMUTING_PROJECTION_NULL",
    "RANDOM_LOW_RANK_LINEAR_NULL",
    "DIAGONAL_LINEAR_NULL",
    "FAMILY_LABEL_PROXY_NULL",
    "CLOCK_BLOCK_PROXY_NULL",
}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_LINEAR_SPECIFICITY_METRIC_REGISTRY_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    add("doc_exists", DOC.exists())
    add("metric_csv_exists", CSV.exists())
    add("summary_exists", SUMMARY.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_LINEAR_SPECIFICITY_METRIC_REGISTRY_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)

    add("required_metrics_present", REQUIRED_METRICS.issubset(set(df["MetricID"])))
    add("all_required_before_linear_freeze", df["RequiredBeforeLinearFreeze"].astype(bool).all())
    add("no_target_residuals", not df["UsesTargetResiduals"].astype(bool).any())
    add("no_p5c_v3_outcome", not df["UsesP5Cv3Outcome"].astype(bool).any())
    add("no_scoring_authorized", not df["ScoringAuthorized"].astype(bool).any())
    add("linear_not_frozen", not bool(summary["LinearCandidateFrozen"].iloc[0]))
    add("delta_c_tau_not_generated", not bool(summary["DeltaCTauGenerated"].iloc[0]))
    add("p_taucov_scoring_not_authorized", not bool(summary["PTauCovScoringAuthorized"].iloc[0]))
    nulls = set(str(summary["PrescoreNulls"].iloc[0]).split(";"))
    add("required_nulls_declared", REQUIRED_NULLS.issubset(nulls))
    for phrase in [
        "M1_NONCOMMUTATOR_SHARE",
        "M5_NULL_SEPARATION_MARGIN",
        "SHUFFLED_BRANCH_OPERATOR",
        "COMMUTING_PROJECTION_NULL",
        "The linear metric registry proves a Tau covariance signal",
    ]:
        add(f"doc_contains_{phrase[:32]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_LINEAR_SPECIFICITY_METRIC_REGISTRY_INVALID")
        print(failed.to_string(index=False))
        return 1

    print("P_TAUCOV_LINEAR_SPECIFICITY_METRIC_REGISTRY_VALID_PRESCORE_ONLY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
