#!/usr/bin/env python3
"""Build the Tau Core A2 route decision matrix.

This consolidates the two next-step routes after the locked A2 support ladder:
public-covariance upgrade and branch-scatter/systematic registration. It does
not modify K2, fit K1, or authorize measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SUPPORT = EVIDENCE / "source_split_likelihood_native_support_ladder_summary.csv"
PUBLIC_POLICY = EVIDENCE / "public_covariance_policy_readiness.csv"
PUBLIC_UPGRADE = EVIDENCE / "public_covariance_upgrade_readiness.csv"
SHRINKAGE = EVIDENCE / "registered_shrinkage_activation_summary.csv"
SHRINKAGE_PREFLIGHT = EVIDENCE / "registered_shrinkage_future_preflight_summary.csv"
BRANCH_PROMOTION = EVIDENCE / "source_split_likelihood_native_branch_scatter_promotion_summary.csv"
ROUTE = EVIDENCE / "source_split_likelihood_native_covariance_route_summary.csv"
BRANCH_CALIBRATION = EVIDENCE / "branch_scatter_independent_calibration_summary.csv"

OUT = EVIDENCE / "tau_core_a2_route_decision_matrix.csv"
SUMMARY = EVIDENCE / "tau_core_a2_route_decision_summary.csv"
DOC = DOCS / "tau_core_a2_route_decision_matrix.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    support = first(SUPPORT)
    public_policy = first(PUBLIC_POLICY)
    public_upgrade = first(PUBLIC_UPGRADE)
    shrinkage = first(SHRINKAGE)
    shrinkage_preflight = first(SHRINKAGE_PREFLIGHT)
    branch = first(BRANCH_PROMOTION)
    route = first(ROUTE)
    branch_calibration = first(BRANCH_CALIBRATION)

    rows = [
        {
            "RouteID": "R1_PUBLIC_FULL_COVARIANCE",
            "RouteClass": "preferred_measurement_route",
            "CurrentStatus": (
                "BLOCKED"
                if not truthy(public_upgrade["MeasurementValidationRouteAvailable"])
                else "READY"
            ),
            "A2VsK1Status": support["K2VsK1Status"],
            "A2VsPolynomialStatus": support["K2VsPolynomialStatus"],
            "CanSupportCurrentPreflight": truthy(public_policy["PreferredRerunReady"]),
            "CanSupportMeasurementValidation": truthy(public_upgrade["MeasurementValidationRouteAvailable"]),
            "PrimaryBlocker": "full public likelihood-native covariance and cross-covariance route missing",
            "AllowedClaim": "no stronger claim from this route yet",
            "NextAction": "implement or import full likelihood-native public covariance transform before scorecard interpretation",
            "ClaimBoundary": "tau_core_a2_route_decision_no_measurement_validation",
        },
        {
            "RouteID": "R2_REGISTERED_SHRINKAGE",
            "RouteClass": "future_preflight_public_proxy",
            "CurrentStatus": (
                "FUTURE_PREFLIGHT_ONLY"
                if truthy(shrinkage["RegisteredShrinkagePreflightActivationAllowed"])
                else "BLOCKED"
            ),
            "A2VsK1Status": (
                "SUPPORTIVE_PREFLIGHT"
                if truthy(shrinkage_preflight["K2ImprovesOverK1"])
                else "WEAKENING"
            ),
            "A2VsPolynomialStatus": (
                "SUPPORTIVE_PREFLIGHT"
                if truthy(shrinkage_preflight["K2BeatsBestPoly"])
                else "WEAKENING_PUBLIC_PROXY"
            ),
            "CanSupportCurrentPreflight": truthy(shrinkage["RegisteredShrinkagePreflightActivationAllowed"]),
            "CanSupportMeasurementValidation": False,
            "PrimaryBlocker": str(shrinkage["PrimaryMeasurementBlocker"]),
            "AllowedClaim": "future preflight sensitivity route only",
            "NextAction": "keep as registered sensitivity route; do not use as validation unless polynomial/public covariance blockers clear",
            "ClaimBoundary": "tau_core_a2_route_decision_no_measurement_validation",
        },
        {
            "RouteID": "R3_BRANCH_SCATTER_SYSTEMATIC",
            "RouteClass": "declared_preflight_bridge",
            "CurrentStatus": (
                "INDEPENDENTLY_CALIBRATED_PREFLIGHT_SUPPORT"
                if truthy(branch_calibration["IndependentCalibrationPreflightSupported"])
                else "DECLARED_PREFLIGHT_SUPPORT"
                if truthy(branch["PreflightBenchmarkPromotionAllowed"])
                and not truthy(branch["MeasurementValidationPromotionAllowed"])
                else "MIXED_OR_BLOCKED"
            ),
            "A2VsK1Status": support["K2VsK1Status"],
            "A2VsPolynomialStatus": support["K2VsPolynomialStatus"],
            "CanSupportCurrentPreflight": truthy(branch["PreflightBenchmarkPromotionAllowed"]),
            "CanSupportMeasurementValidation": truthy(branch["MeasurementValidationPromotionAllowed"]),
            "PrimaryBlocker": (
                "independent reconstruction-family calibration is preflight only; public full covariance still missing"
                if truthy(branch_calibration["IndependentCalibrationPreflightSupported"])
                else "branch scatter is not public full covariance or independently registered systematic yet"
            ),
            "AllowedClaim": (
                "independently calibrated preflight support route"
                if truthy(branch["PreflightBenchmarkPromotionAllowed"])
                and not truthy(branch["MeasurementValidationPromotionAllowed"])
                else "declared preflight support route"
            ),
            "NextAction": "use this as calibrated preflight bridge; keep Phase II focused on full public covariance",
            "ClaimBoundary": "tau_core_a2_route_decision_no_measurement_validation",
        },
        {
            "RouteID": "R4_FORBIDDEN_POST_HOC_ROUTE",
            "RouteClass": "forbidden",
            "CurrentStatus": "FORBIDDEN",
            "A2VsK1Status": "not_applicable",
            "A2VsPolynomialStatus": "not_applicable",
            "CanSupportCurrentPreflight": False,
            "CanSupportMeasurementValidation": False,
            "PrimaryBlocker": "route selected or tuned after inspecting A2-vs-control score",
            "AllowedClaim": "none",
            "NextAction": "do not use",
            "ClaimBoundary": "tau_core_a2_route_decision_no_measurement_validation",
        },
    ]
    matrix = pd.DataFrame(rows)
    matrix.to_csv(OUT, index=False)

    current_preflight_routes = int(matrix["CanSupportCurrentPreflight"].map(truthy).sum())
    measurement_routes = int(matrix["CanSupportMeasurementValidation"].map(truthy).sum())
    branch_preflight = matrix[matrix["RouteID"].eq("R3_BRANCH_SCATTER_SYSTEMATIC")].iloc[0]
    public_ready = matrix[matrix["RouteID"].eq("R1_PUBLIC_FULL_COVARIANCE")].iloc[0]
    summary = pd.DataFrame(
        [
            {
                "DecisionID": "TAU_CORE_A2_ROUTE_DECISION_MATRIX_V1",
                "Routes": len(matrix),
                "CurrentPreflightRoutes": current_preflight_routes,
                "MeasurementValidationRoutes": measurement_routes,
                "RecommendedNextRoute": "R3_BRANCH_SCATTER_SYSTEMATIC",
                "PublicCovarianceStatus": public_ready["CurrentStatus"],
                "RegisteredShrinkageStatus": matrix[matrix["RouteID"].eq("R2_REGISTERED_SHRINKAGE")].iloc[0][
                    "CurrentStatus"
                ],
                "BranchScatterStatus": branch_preflight["CurrentStatus"],
                "CurrentBestSupportedRoute": route["CurrentBestSupportedRoute"],
                "MeasurementValidationAllowed": False,
                "StrongestAllowedClaim": (
                    "locked A2 has independently calibrated preflight support through the branch-scatter/systematic bridge"
                    if truthy(branch_calibration["IndependentCalibrationPreflightSupported"])
                    else "locked A2 has declared preflight support through the branch-scatter/systematic bridge"
                ),
                "PrimaryResidualRisk": "public covariance route remains weak and all-depth polynomial tension remains unresolved",
                "NextAction": "keep Phase II focused on full public covariance while preserving the calibrated branch-scatter preflight bridge",
                "ClaimBoundary": "tau_core_a2_route_decision_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tau Core A2 Route Decision Matrix",
        "",
        "Status: route decision for locked A2 preflight only. Measurement validation remains closed.",
        "",
        "## Decision",
        "",
        f"- Recommended next route: {summary.iloc[0]['RecommendedNextRoute']}",
        f"- Current best supported route: {summary.iloc[0]['CurrentBestSupportedRoute']}",
        f"- Current preflight routes: {current_preflight_routes}",
        f"- Measurement-validation routes: {measurement_routes}",
        f"- Strongest allowed claim: {summary.iloc[0]['StrongestAllowedClaim']}",
        "",
        "## Routes",
        "",
    ]
    for _, row in matrix.iterrows():
        lines.extend(
            [
                f"### {row['RouteID']}",
                "",
                f"- Status: {row['CurrentStatus']}",
                f"- Class: {row['RouteClass']}",
                f"- Current preflight: {row['CanSupportCurrentPreflight']}",
                f"- Measurement validation: {row['CanSupportMeasurementValidation']}",
                f"- Primary blocker: {row['PrimaryBlocker']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
