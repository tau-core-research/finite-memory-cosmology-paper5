#!/usr/bin/env python3
"""Build a compact covariance-route scorecard for likelihood-native K2."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

SCALE = EVIDENCE / "source_split_likelihood_native_scale_covariance_summary.csv"
BRANCH = EVIDENCE / "source_split_likelihood_native_branch_scatter_summary.csv"
PUBLIC_PROXY = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_summary.csv"
CROSS = EVIDENCE / "source_split_likelihood_native_cross_covariance_summary.csv"
OUT = EVIDENCE / "source_split_likelihood_native_covariance_route_scorecard.csv"
SUMMARY = EVIDENCE / "source_split_likelihood_native_covariance_route_summary.csv"


def status_from_flags(improves: bool, beats_poly: bool) -> str:
    if improves and beats_poly:
        return "K2_COMPETITIVE_PREFLIGHT"
    if improves:
        return "K2_IMPROVES_OVER_K1_BUT_CONTROLS_DOMINATE"
    return "K2_WEAKENING"


def route_row(route_id: str, route_class: str, source: str, row: pd.Series, note: str) -> dict[str, object]:
    improves = bool(str(row["K2ImprovesOverK1"]).lower() == "true")
    beats_poly = bool(str(row["K2BeatsBestPoly"]).lower() == "true")
    return {
        "RouteID": route_id,
        "RouteClass": route_class,
        "SourceRow": source,
        "BestModel": row["BestModel"],
        "K1AIC": float(row["K1AIC"]),
        "K2AIC": float(row["K2AIC"]),
        "BestPolyAIC": float(row["BestPolyAIC"]),
        "DeltaAIC_K2_minus_K1": float(row["DeltaAIC_K2_minus_K1"]),
        "DeltaAIC_K2_minus_BestPoly": float(row["DeltaAIC_K2_minus_BestPoly"]),
        "K2ImprovesOverK1": improves,
        "K2BeatsBestPoly": beats_poly,
        "RouteStatus": status_from_flags(improves, beats_poly),
        "Note": note,
        "ClaimBoundary": "covariance_route_scorecard_no_measurement_validation",
    }


def main() -> None:
    rows: list[dict[str, object]] = []

    if SCALE.exists():
        scale = pd.read_csv(SCALE)
        for case in ["diag_native_sigma", "diag_target_fraction_floor_25pct"]:
            match = scale[scale["CovarianceCase"].eq(case)]
            if not match.empty:
                rows.append(
                    route_row(
                        route_id=case.upper(),
                        route_class="scale_covariance_sensitivity",
                        source=case,
                        row=match.iloc[0],
                        note=(
                            "native weakening baseline"
                            if case == "diag_native_sigma"
                            else "target-fraction floor sensitivity, not independent covariance"
                        ),
                    )
                )

    if BRANCH.exists():
        branch = pd.read_csv(BRANCH)
        for _, item in branch.iterrows():
            rows.append(
                route_row(
                    route_id=f"BRANCH_SCATTER::{item['CovarianceCase']}",
                    route_class="declared_preflight_benchmark",
                    source=str(item["CovarianceCase"]),
                    row=item,
                    note="branch scatter route; strongest current K2-supportive preflight path",
                )
            )

    if PUBLIC_PROXY.exists():
        public_proxy = pd.read_csv(PUBLIC_PROXY)
        if not public_proxy.empty:
            item = public_proxy.iloc[0]
            rows.append(
                route_row(
                    route_id="PUBLIC_SN_BAO_PROPAGATED_PROXY",
                    route_class="public_covariance_proxy",
                    source=str(item["CovarianceID"]),
                    row=item,
                    note="uses public raw covariance inputs but simplified transform and zero SN-BAO cross-covariance",
                )
            )

    if CROSS.exists():
        cross = pd.read_csv(CROSS)
        if not cross.empty:
            best_for_k2 = cross.sort_values("DeltaAIC_K2_minus_BestPoly").iloc[0]
            rows.append(
                route_row(
                    route_id="PUBLIC_PROXY_CROSS_COV_BEST_CASE",
                    route_class="public_covariance_proxy_sensitivity",
                    source=f"rho_cross={best_for_k2['RhoCross']}",
                    row=best_for_k2,
                    note="best K2-vs-polynomial case under row-aligned cross-covariance sensitivity",
                )
            )

    scorecard = pd.DataFrame(rows)
    scorecard.to_csv(OUT, index=False)

    total = len(scorecard)
    k2_competitive = int(scorecard["K2BeatsBestPoly"].sum()) if total else 0
    k2_improves = int(scorecard["K2ImprovesOverK1"].sum()) if total else 0
    branch_competitive = int(
        (
            scorecard["RouteClass"].eq("declared_preflight_benchmark")
            & scorecard["K2BeatsBestPoly"].eq(True)
        ).sum()
    ) if total else 0
    public_proxy_competitive = int(
        (
            scorecard["RouteClass"].str.contains("public_covariance_proxy", na=False)
            & scorecard["K2BeatsBestPoly"].eq(True)
        ).sum()
    ) if total else 0
    summary = pd.DataFrame(
        [
            {
                "Routes": total,
                "RoutesWhereK2ImprovesOverK1": k2_improves,
                "RoutesWhereK2BeatsBestPoly": k2_competitive,
                "BranchScatterCompetitiveRoutes": branch_competitive,
                "PublicProxyCompetitiveRoutes": public_proxy_competitive,
                "CurrentBestSupportedRoute": "BRANCH_SCATTER_DECLARED_PREFLIGHT",
                "PrimaryBlockingIssue": "public_proxy_not_yet_competitive_with_polynomial_controls",
                "NextAction": "upgrade public covariance transform or independently justify branch-scatter response-scale route",
                "Interpretation": "k2_support_is_route_dependent_branch_scatter_strong_public_proxy_mixed",
                "ClaimBoundary": "covariance_route_scorecard_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
