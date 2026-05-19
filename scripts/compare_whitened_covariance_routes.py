#!/usr/bin/env python3
"""Compare whitened covariance-route preflight outcomes."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROUTES = [
    (
        "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        EVIDENCE / "whitened_standardized_branch_contrast_summary.csv",
        "public_covariance_proxy_zero_sn_bao_cross_covariance",
    ),
    (
        "REGISTERED_SHRINKAGE_WHITENED",
        EVIDENCE / "registered_shrinkage_whitened_branch_contrast_summary.csv",
        "registered_shrinkage_preflight_covariance",
    ),
]

OUT = EVIDENCE / "whitened_covariance_route_comparison.csv"
OUT_SUMMARY = EVIDENCE / "whitened_covariance_route_comparison_summary.csv"
OUT_DOC = DOCS / "whitened_covariance_route_comparison.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    rows = []
    for route_id, path, cov_status in ROUTES:
        row = pd.read_csv(path).iloc[0]
        rows.append(
            {
                "ComparisonID": "WHITENED_COVARIANCE_ROUTE_COMPARISON_V1",
                "RouteID": route_id,
                "SourceFile": str(path.relative_to(ROOT)),
                "CovarianceRouteStatus": cov_status,
                "Rows": int(row["Rows"]),
                "BestModel": row["BestModel"],
                "K1AIC": float(row["K1AIC"]),
                "K2AIC": float(row["K2AIC"]),
                "BestPolyAIC": float(row["BestPolyAIC"]),
                "DeltaAIC_K2_minus_K1": float(row["DeltaAIC_K2_minus_K1"]),
                "DeltaAIC_K2_minus_BestPoly": float(row["DeltaAIC_K2_minus_BestPoly"]),
                "K2ImprovesOverK1": truthy(row["K2ImprovesOverK1"]),
                "K2BeatsBestPoly": truthy(row["K2BeatsBestPoly"]),
                "PositiveDefinite": truthy(row.get("PositiveDefinite", row.get("CovariancePositiveDefinite", False))),
                "MeasurementValidationAllowed": False,
                "RouteFinding": (
                    "k2_beats_k1_but_polynomial_remains_stronger"
                    if truthy(row["K2ImprovesOverK1"]) and not truthy(row["K2BeatsBestPoly"])
                    else "mixed_or_weakening"
                ),
                "ClaimBoundary": "whitened_covariance_route_comparison_no_measurement_validation",
            }
        )
    comparison = pd.DataFrame(rows)
    comparison.to_csv(OUT, index=False)

    k2_over_k1_routes = int(comparison["K2ImprovesOverK1"].sum())
    k2_over_poly_routes = int(comparison["K2BeatsBestPoly"].sum())
    summary = pd.DataFrame(
        [
            {
                "ComparisonID": "WHITENED_COVARIANCE_ROUTE_COMPARISON_V1",
                "Routes": len(comparison),
                "PositiveDefiniteRoutes": int(comparison["PositiveDefinite"].sum()),
                "K2ImprovesOverK1Routes": k2_over_k1_routes,
                "K2BeatsBestPolyRoutes": k2_over_poly_routes,
                "AllRoutesK2ImproveOverK1": k2_over_k1_routes == len(comparison),
                "AnyRouteK2BeatsBestPoly": k2_over_poly_routes > 0,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "WHITENED_ROUTES_SUPPORT_K2_OVER_K1_POLYNOMIAL_BLOCK_REMAINS"
                    if k2_over_k1_routes == len(comparison) and k2_over_poly_routes == 0
                    else "WHITENED_ROUTES_MIXED"
                ),
                "StrongestAllowedClaim": (
                    "both whitened covariance routes remove the K1 no-memory advantage, but neither resolves the polynomial-control tension"
                ),
                "PrimaryResidualRisk": (
                    "A2/K2 distinctiveness still requires a likelihood-native benchmark where polynomial/control flexibility is constrained independently"
                ),
                "NextAction": (
                    "diagnose weighted polynomial dominance row-by-row and with predeclared complexity penalties/cross-validation before any stronger interpretation"
                ),
                "ClaimBoundary": "whitened_covariance_route_comparison_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Whitened Covariance Route Comparison",
                "",
                "Status: preflight comparison; no measurement-validation claim.",
                "",
                "Both implemented whitened routes support K2 over the frozen K1 no-memory baseline, but the weighted polynomial controls remain stronger under the current small diagnostic vector.",
                "",
                "## Outputs",
                "",
                f"- Comparison: `{OUT.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Interpretation",
                "",
                "The current bottleneck is no longer a simple K1 no-memory dominance. The remaining issue is whether flexible polynomial controls are fair physical nulls, over-flexible diagnostic controls, or genuinely better descriptions of the current packet.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
