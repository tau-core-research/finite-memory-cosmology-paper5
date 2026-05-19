#!/usr/bin/env python3
"""Build a compact support ladder for likelihood-native K2 preflight results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

ROUTE_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_covariance_route_summary.csv"
GAP_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_covariance_gap_summary.csv"
POLY_CV = ROOT / "evidence" / "source_split_likelihood_native_polynomial_cv_summary.csv"
PROMOTION = ROOT / "evidence" / "source_split_likelihood_native_branch_scatter_promotion_summary.csv"
PUBLIC_PROXY = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_summary.csv"

OUT = ROOT / "evidence" / "source_split_likelihood_native_support_ladder.csv"
OUT_SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_support_ladder_summary.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    route = pd.read_csv(ROUTE_SUMMARY).iloc[0]
    gap = pd.read_csv(GAP_SUMMARY).iloc[0]
    cv = pd.read_csv(POLY_CV)
    promotion = pd.read_csv(PROMOTION).iloc[0]
    public_proxy = pd.read_csv(PUBLIC_PROXY).iloc[0]

    comparisons = cv[cv["ModelID"].eq("CV_COMPARISON")].copy()
    cv_rows = int(len(comparisons))
    cv_k2_over_k1 = int(comparisons["K2ImprovesOverK1"].map(bool_text).sum())
    cv_k2_over_poly = int(comparisons["K2BeatsBestPoly"].map(bool_text).sum())
    public_cv = comparisons[comparisons["SigmaRoute"].eq("public_proxy_diag")]
    public_cv_over_poly = int(public_cv["K2BeatsBestPoly"].map(bool_text).sum())

    ladder_rows = [
        {
            "LevelID": "L1_K2_VS_K1",
            "Question": "Does locked K2 improve over frozen K1/no-memory?",
            "Evidence": (
                f"route scorecard {int(route['RoutesWhereK2ImprovesOverK1'])}/"
                f"{int(route['Routes'])}; row gap public {int(gap['RowsWhereK2PublicContributionBelowK1'])}/"
                f"{int(gap['Rows'])}; CV {cv_k2_over_k1}/{cv_rows}"
            ),
            "Status": "SUPPORTIVE_PREFLIGHT",
            "Interpretation": "K2 consistently improves over K1/no-memory across current route, row, and CV diagnostics.",
            "BlockingIssue": "none at K2-vs-K1 preflight level",
            "ClaimBoundary": "support_ladder_no_measurement_validation",
        },
        {
            "LevelID": "L2_K2_VS_POLYNOMIAL_CONTROLS",
            "Question": "Does locked K2 beat flexible polynomial controls?",
            "Evidence": (
                f"route scorecard {int(route['RoutesWhereK2BeatsBestPoly'])}/{int(route['Routes'])}; "
                f"public-proxy row gap {int(gap['RowsWhereK2PublicContributionBelowBestPoly'])}/{int(gap['Rows'])}; "
                f"CV {cv_k2_over_poly}/{cv_rows}"
            ),
            "Status": "MIXED_CONDITIONAL_SUPPORT",
            "Interpretation": "K2 beats polynomial controls on branch-scatter routes and most CV comparisons, but not on the public-proxy in-sample route.",
            "BlockingIssue": "public_proxy_polynomial_controls_remain_competitive",
            "ClaimBoundary": "support_ladder_no_measurement_validation",
        },
        {
            "LevelID": "L3_PUBLIC_COVARIANCE_ROUTE",
            "Question": "Is the public covariance proxy sufficient for stronger interpretation?",
            "Evidence": (
                f"public proxy K2 improves over K1={bool_text(public_proxy['K2ImprovesOverK1'])}; "
                f"K2 beats best polynomial={bool_text(public_proxy['K2BeatsBestPoly'])}; "
                f"public CV beats polynomial {public_cv_over_poly}/{len(public_cv)}"
            ),
            "Status": "WEAKENING_PUBLIC_PROXY",
            "Interpretation": "The public covariance proxy is useful but still mixed; it does not yet support measurement validation.",
            "BlockingIssue": "full_likelihood_covariance_or_better_public_transform_missing",
            "ClaimBoundary": "support_ladder_no_measurement_validation",
        },
        {
            "LevelID": "L4_BRANCH_SCATTER_ROUTE",
            "Question": "Can branch scatter be used as the declared preflight benchmark?",
            "Evidence": (
                f"branch-scatter competitive routes {int(route['BranchScatterCompetitiveRoutes'])}; "
                f"preflight promotion allowed={bool_text(promotion['PreflightBenchmarkPromotionAllowed'])}; "
                f"measurement promotion allowed={bool_text(promotion['MeasurementValidationPromotionAllowed'])}"
            ),
            "Status": "DECLARED_PREFLIGHT_SUPPORT",
            "Interpretation": "Branch scatter is the strongest current K2-supportive route, but it is not public full covariance.",
            "BlockingIssue": "independent_systematic_or_public_full_covariance_missing",
            "ClaimBoundary": "support_ladder_no_measurement_validation",
        },
        {
            "LevelID": "L5_MEASUREMENT_VALIDATION",
            "Question": "Is the finite-memory projection hypothesis measurement-validated?",
            "Evidence": (
                f"measurement validation promotion allowed={bool_text(promotion['MeasurementValidationPromotionAllowed'])}; "
                f"primary route blocker={route['PrimaryBlockingIssue']}"
            ),
            "Status": "BLOCKED",
            "Interpretation": "Current results are operational and conditionally supportive, but not measurement validation.",
            "BlockingIssue": "public_covariance_proxy_not_yet_competitive_with_polynomial_controls",
            "ClaimBoundary": "support_ladder_no_measurement_validation",
        },
    ]
    ladder = pd.DataFrame(ladder_rows)
    ladder.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "SupportLadderRows": len(ladder),
                "CurrentStrongestStatus": "DECLARED_PREFLIGHT_SUPPORT",
                "K2VsK1Status": "SUPPORTIVE_PREFLIGHT",
                "K2VsPolynomialStatus": "MIXED_CONDITIONAL_SUPPORT",
                "PublicCovarianceStatus": "WEAKENING_PUBLIC_PROXY",
                "MeasurementValidationStatus": "BLOCKED",
                "PrimaryNextAction": "upgrade public covariance transform or independently register branch-scatter/systematic route",
                "Interpretation": "k2_is_strengthened_relative_to_k1_and_conditionally_against_polynomial_controls_but_not_measurement_validated",
                "ClaimBoundary": "support_ladder_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
