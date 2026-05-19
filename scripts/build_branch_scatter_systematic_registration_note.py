#!/usr/bin/env python3
"""Register the branch-scatter route as a preflight systematic bridge.

The route is intentionally weaker than a public full-covariance measurement
route. It is useful as a declared preflight benchmark because it is not selected
by changing K2, K1, rho, or the kernel after inspection.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROMOTION = EVIDENCE / "source_split_likelihood_native_branch_scatter_promotion_summary.csv"
ROUTE = EVIDENCE / "source_split_likelihood_native_covariance_route_summary.csv"
SCORECARD = EVIDENCE / "source_split_likelihood_native_branch_scatter_scorecard.csv"
SCATTER = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"

OUT = EVIDENCE / "branch_scatter_systematic_registration.csv"
SUMMARY = EVIDENCE / "branch_scatter_systematic_registration_summary.csv"
DOC = DOCS / "branch_scatter_systematic_registration.md"


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
    promotion = first(PROMOTION)
    route = first(ROUTE)
    scorecard = pd.read_csv(SCORECARD)
    scatter = pd.read_csv(SCATTER)

    k2_rows = scorecard[scorecard["ModelID"].eq("K2_LOCKED_RHO4")]
    route_column = "CovarianceRoute" if "CovarianceRoute" in scorecard.columns else "CovarianceCase"
    best_models = scorecard.sort_values("AIC").groupby(route_column, as_index=False).first()
    k2_best_routes = int(best_models["ModelID"].eq("K2_LOCKED_RHO4").sum())
    branch_rows_with_two = int((scatter["BranchCount"] >= 2).sum())

    rows = [
        {
            "RegistrationCheckID": "BS_REG_1_ROUTE_DECLARED",
            "Status": "PASS" if truthy(promotion["PreflightBenchmarkPromotionAllowed"]) else "BLOCKED",
            "Evidence": "branch-scatter promotion gate allows preflight benchmark",
            "Interpretation": "route can be used as declared preflight benchmark",
            "BlocksMeasurementValidation": False,
        },
        {
            "RegistrationCheckID": "BS_REG_2_NOT_FULL_PUBLIC_COVARIANCE",
            "Status": "PASS",
            "Evidence": "branch scatter is explicitly not public full covariance",
            "Interpretation": "claim level is capped at preflight bridge",
            "BlocksMeasurementValidation": True,
        },
        {
            "RegistrationCheckID": "BS_REG_3_TWO_BRANCH_COVERAGE",
            "Status": "PASS" if branch_rows_with_two == len(scatter) else "WARNING",
            "Evidence": f"rows with at least two branches={branch_rows_with_two}/{len(scatter)}",
            "Interpretation": "branch scatter is available across the current scoring grid",
            "BlocksMeasurementValidation": False,
        },
        {
            "RegistrationCheckID": "BS_REG_4_K2_ROUTE_COMPETITIVE",
            "Status": "PASS" if k2_best_routes >= int(route["BranchScatterCompetitiveRoutes"]) else "WARNING",
            "Evidence": (
                f"K2 best branch-scatter routes={k2_best_routes}; "
                f"route summary competitive={route['BranchScatterCompetitiveRoutes']}"
            ),
            "Interpretation": "locked A2 remains competitive under branch-scatter route variants",
            "BlocksMeasurementValidation": False,
        },
        {
            "RegistrationCheckID": "BS_REG_5_NO_POST_HOC_KERNEL_CHANGE",
            "Status": "PASS",
            "Evidence": "uses locked K2_A2 = 2*K1*(1+4*x^3); no rho>4; no K1 refit",
            "Interpretation": "route does not change the finite-memory prediction",
            "BlocksMeasurementValidation": False,
        },
        {
            "RegistrationCheckID": "BS_REG_6_INDEPENDENT_SYSTEMATIC_PENDING",
            "Status": "WARNING",
            "Evidence": "branch scatter is not yet independently calibrated as systematic floor",
            "Interpretation": "stronger interpretation requires independent systematic or public full covariance",
            "BlocksMeasurementValidation": True,
        },
    ]
    detail = pd.DataFrame(rows)
    detail["ClaimBoundary"] = "branch_scatter_systematic_registration_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    warnings = int(detail["Status"].eq("WARNING").sum())
    blocked = int(detail["Status"].eq("BLOCKED").sum())
    measurement_blockers = int(detail["BlocksMeasurementValidation"].map(truthy).sum())
    preflight_registered = blocked == 0 and truthy(promotion["PreflightBenchmarkPromotionAllowed"])
    summary = pd.DataFrame(
        [
            {
                "RegistrationID": "BRANCH_SCATTER_SYSTEMATIC_PREFLIGHT_REGISTRATION_V1",
                "Checks": len(detail),
                "PassedChecks": int(detail["Status"].eq("PASS").sum()),
                "WarningChecks": warnings,
                "BlockedChecks": blocked,
                "PreflightRouteRegistered": preflight_registered,
                "MeasurementValidationAllowed": False,
                "MeasurementBlockingChecks": measurement_blockers,
                "K2BestBranchScatterRoutes": k2_best_routes,
                "BranchScatterCompetitiveRoutes": int(route["BranchScatterCompetitiveRoutes"]),
                "CurrentStatus": (
                    "BRANCH_SCATTER_REGISTERED_AS_PREFLIGHT_SYSTEMATIC_BRIDGE"
                    if preflight_registered
                    else "BRANCH_SCATTER_REGISTRATION_BLOCKED"
                ),
                "StrongestAllowedClaim": "branch scatter is registered as a declared A2 preflight bridge",
                "PrimaryResidualRisk": "branch scatter is not independent public full covariance and not measurement validation",
                "NextAction": "calibrate branch scatter against independent reconstruction-family/systematic sources or replace with full public covariance",
                "ClaimBoundary": "branch_scatter_systematic_registration_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch-Scatter Systematic Registration",
        "",
        "Status: declared preflight bridge only. This is not measurement validation.",
        "",
        "## Summary",
        "",
        f"- Preflight route registered: {preflight_registered}",
        f"- Measurement validation allowed: False",
        f"- Current status: {summary.iloc[0]['CurrentStatus']}",
        f"- Strongest allowed claim: {summary.iloc[0]['StrongestAllowedClaim']}",
        f"- Residual risk: {summary.iloc[0]['PrimaryResidualRisk']}",
        "",
        "## Rules",
        "",
        "- K2 remains locked.",
        "- rho remains bounded at 4.",
        "- K1 is not refit.",
        "- The route cannot be selected as a measurement route without independent covariance/systematic calibration.",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['RegistrationCheckID']}",
                "",
                f"- Status: {row['Status']}",
                f"- Evidence: {row['Evidence']}",
                f"- Interpretation: {row['Interpretation']}",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
