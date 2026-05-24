#!/usr/bin/env python3
"""Summarize the expanded parent-operator P-TauCov scorecard failure mode."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard_summary.csv"
GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_survival_gates.csv"
NULLS = ROOT / "evidence/p_taucov_expanded_parent_operator_null_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_expanded_parent_operator_oos_scorecard.csv"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_failure_analysis.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_failure_analysis_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_failure_analysis.md"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FAILURE_ANALYSIS_v1"
STATUS = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FAILURE_LOCALIZED_NO_RESCUE"
CLAIM_BOUNDARY = "post_score_failure_analysis_no_new_scoring_no_rescue"


def main() -> int:
    summary = pd.read_csv(SUMMARY).iloc[0]
    gates = pd.read_csv(GATES)
    nulls = pd.read_csv(NULLS).sort_values("PrimaryOOSDeltaNLL_BaselineMinusKernel", ascending=False)
    oos = pd.read_csv(OOS)
    primary = oos[oos["PrimaryOOS"]].copy()

    primary_delta = float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"])
    strongest = nulls.iloc[0]
    strongest_delta = float(strongest["PrimaryOOSDeltaNLL_BaselineMinusKernel"])
    margin_vs_strongest = primary_delta - strongest_delta
    positive = primary[primary["DeltaNLL_BaselineMinusKernel"] > 0.0]
    largest_fold = positive.sort_values("DeltaNLL_BaselineMinusKernel", ascending=False).iloc[0]
    largest_share = float(largest_fold["DeltaNLL_BaselineMinusKernel"] / positive["DeltaNLL_BaselineMinusKernel"].sum())
    failed_gates = gates.loc[~gates["Passed"].astype(bool), "GateID"].astype(str).tolist()
    alpha_zero_folds = int((primary["Alpha"].astype(float) <= 0.0).sum())

    rows = [
        {
            "AuditID": AUDIT_ID,
            "FindingID": "F1_STRONG_POSITIVE_PRIMARY_OOS",
            "Value": primary_delta,
            "Comparator": 0.0,
            "PassedAsPositiveSignal": primary_delta > 0.0,
            "Interpretation": "expanded candidate carries covariance-level signal against diagonal baseline",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "AuditID": AUDIT_ID,
            "FindingID": "F2_GENERIC_SMOOTH_PSD_BEATS_PRIMARY",
            "Value": margin_vs_strongest,
            "Comparator": str(strongest["KernelID"]),
            "PassedAsPositiveSignal": False,
            "Interpretation": "primary object is not Tau-specific enough because a generic smooth PSD null is stronger",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "AuditID": AUDIT_ID,
            "FindingID": "F3_DOMINANCE_REMAINS",
            "Value": largest_share,
            "Comparator": str(largest_fold["FoldID"]),
            "PassedAsPositiveSignal": largest_share <= 0.60,
            "Interpretation": "positive score is too concentrated in one primary fold",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
        {
            "AuditID": AUDIT_ID,
            "FindingID": "F4_ALPHA_INSTABILITY_REMAINS",
            "Value": float(alpha_zero_folds),
            "Comparator": "primary folds with alpha <= 0",
            "PassedAsPositiveSignal": alpha_zero_folds == 0,
            "Interpretation": "fitted deformation scale is not stable across primary folds",
            "ClaimBoundary": CLAIM_BOUNDARY,
        },
    ]
    table = pd.DataFrame(rows)
    table.to_csv(OUT, index=False)
    out_summary = pd.DataFrame(
        [
            {
                "AuditID": AUDIT_ID,
                "Status": STATUS,
                "PrimaryOOSDeltaNLL": primary_delta,
                "StrongestNullID": str(strongest["KernelID"]),
                "StrongestNullDeltaNLL": strongest_delta,
                "PrimaryMinusStrongestNull": margin_vs_strongest,
                "FailedGates": ";".join(failed_gates),
                "LargestPositiveFold": str(largest_fold["FoldID"]),
                "LargestPositiveFoldShare": largest_share,
                "AlphaZeroPrimaryFolds": alpha_zero_folds,
                "SurvivalClaimAuthorized": False,
                "RecommendedNextGate": "derive_non_smooth_parent_hessian_specific_constraint_before_any_new_scoring",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    out_summary.to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Expanded Parent-Operator Failure Analysis",
                "",
                f"Status: `{STATUS}`",
                "",
                "This is a post-score failure analysis. It does not introduce a new",
                "score, does not rescue the failed primary scorecard, and does not",
                "authorize survival or Tau Core validation language.",
                "",
                "## What Survived Locally",
                "",
                f"- primary OOS Delta NLL: `{primary_delta}`",
                f"- gates passed: `{int(summary['GatesPassed'])}/{int(summary['GatesTotal'])}`",
                "",
                "The expanded object carries a real covariance-level improvement over",
                "the diagonal baseline.",
                "",
                "## What Failed",
                "",
                f"- strongest null: `{strongest['KernelID']}`",
                f"- strongest null Delta NLL: `{strongest_delta}`",
                f"- primary minus strongest null: `{margin_vs_strongest}`",
                f"- failed gates: `{';'.join(failed_gates)}`",
                f"- largest positive fold share: `{largest_share}`",
                f"- primary folds with alpha <= 0: `{alpha_zero_folds}`",
                "",
                "The decisive failure is not a simple projection-null or morphology-null",
                "duplication. The decisive failure is that a generic smooth PSD covariance",
                "object is stronger than the declared expanded parent-operator object.",
                "",
                "## Consequence",
                "",
                "The next Tau-specific route should not be another covariance-shape",
                "variant. It needs an additional parent-Hessian-specific restriction that",
                "is not reproducible by generic smooth PSD covariance structure.",
                "",
                "Recommended next gate:",
                "",
                "`derive_non_smooth_parent_hessian_specific_constraint_before_any_new_scoring`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
