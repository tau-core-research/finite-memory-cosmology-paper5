#!/usr/bin/env python3
"""Validate the epsilon-P3 morphology-null failure diagnostic."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FOLDS = ROOT / "evidence/p_taucov_epsilon_p3_morphology_null_diagnostic_folds.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_morphology_null_diagnostic_summary.csv"
DOC = ROOT / "docs/p_taucov_epsilon_p3_morphology_null_diagnostic.md"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_morphology_null_diagnostic_validation.csv"

AUDIT_ID = "P_TAUCOV_EPSILON_P3_MORPHOLOGY_NULL_FAILURE_DIAGNOSTIC_VALIDATION"


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

    add(f"exists_{FOLDS.relative_to(ROOT)}", FOLDS.exists())
    add(f"exists_{SUMMARY.relative_to(ROOT)}", SUMMARY.exists())
    add(f"exists_{DOC.relative_to(ROOT)}", DOC.exists())

    if FOLDS.exists() and SUMMARY.exists() and DOC.exists():
        folds = pd.read_csv(FOLDS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_diagnosed", str(summary["Status"]).endswith("MORPHOLOGY_NULL_DOMINANCE_DIAGNOSED"))
        add("survival_not_allowed", bool(summary["SurvivalClaimAllowed"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("morphology_beats_primary", float(summary["MorphologyMinusPrimaryOOSDeltaNLL"]) > 0.0)
        add("high_kernel_correlation_reported", float(summary["KernelCorrelationPrimaryVsMorphologyNull"]) > 0.85)
        add("dominant_family_reported", len(str(summary["DominantFailureFamily"])) > 0)
        add("folds_have_primary_and_morphology_columns", {
            "DeltaNLL_BaselineMinusKernel_Primary",
            "DeltaNLL_BaselineMinusKernel_MorphologyNull",
            "MorphologyMinusPrimaryDeltaNLL",
        }.issubset(set(folds.columns)))
        add("doc_contains_post_failure_diagnostic", "post-failure diagnostic" in doc)
        add("doc_contains_no_new_score_claim", "does not authorize a new" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_EPSILON_P3_MORPHOLOGY_NULL_DIAGNOSTIC_VALID" if ok else "P_TAUCOV_EPSILON_P3_MORPHOLOGY_NULL_DIAGNOSTIC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
