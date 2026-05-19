#!/usr/bin/env python3
"""Row and zone dominance audit for the regularized 200-bootstrap null."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW = EVIDENCE / "regularized_full_pysr_backreaction_200_bridge_row_audit.csv"
SCORE = EVIDENCE / "regularized_full_pysr_backreaction_200_bridge_scorecard.csv"

OUT_ROW = EVIDENCE / "regularized_200_null_dominance_row_audit.csv"
OUT_ZONE = EVIDENCE / "regularized_200_null_dominance_zone_audit.csv"
OUT_SUMMARY = EVIDENCE / "regularized_200_null_dominance_summary.csv"
OUT_DOC = DOCS / "regularized_200_null_dominance_audit.md"

CLAIM_BOUNDARY = "regularized_200_null_dominance_audit_no_measurement_validation"


def depth_zone(z: float) -> str:
    if z < 0.8:
        return "low_depth"
    if z < 1.5:
        return "mid_depth"
    return "high_depth"


def classify(row: pd.Series) -> str:
    values = {
        "K2": float(row["K2Chi2Contribution"]),
        "K1": float(row["K1Chi2Contribution"]),
        "RegularizedNull": float(row["RegularizedNullChi2Contribution"]),
    }
    winner = min(values, key=values.get)
    if winner == "K2":
        return "K2_LOWEST_ROW_CHI2"
    if winner == "K1":
        return "K1_LOWEST_ROW_CHI2"
    return "REGULARIZED_NULL_LOWEST_ROW_CHI2"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    row = pd.read_csv(ROW)
    score = pd.read_csv(SCORE)
    out = row.copy()
    out["DepthZone"] = out["z_grid"].map(depth_zone)
    out["RegularizedNullChi2Contribution"] = (out["WhitenedTarget"] - out["SmokeBackreactionWhitened"]) ** 2
    out["K1Chi2Contribution"] = (out["WhitenedTarget"] - out["K1Whitened"]) ** 2
    out["K2Chi2Contribution"] = (out["WhitenedTarget"] - out["K2LockedWhitened"]) ** 2
    out["DeltaChi2_K2_minus_RegularizedNull_Row"] = (
        out["K2Chi2Contribution"] - out["RegularizedNullChi2Contribution"]
    )
    out["DeltaChi2_K2_minus_K1_Row"] = out["K2Chi2Contribution"] - out["K1Chi2Contribution"]
    out["AbsTarget"] = out["WhitenedTarget"].abs()
    out["AbsRegularizedNull"] = out["SmokeBackreactionWhitened"].abs()
    out["AbsK2"] = out["K2LockedWhitened"].abs()
    out["DominanceClass"] = out.apply(classify, axis=1)
    out["K2BeatsRegularizedNullRow"] = out["K2Chi2Contribution"] < out["RegularizedNullChi2Contribution"]
    out["K2BeatsK1Row"] = out["K2Chi2Contribution"] < out["K1Chi2Contribution"]
    out["RegularizedNullBeatsK2Row"] = out["RegularizedNullChi2Contribution"] < out["K2Chi2Contribution"]
    out["MeasurementValidationAllowed"] = False
    out["ClaimBoundary"] = CLAIM_BOUNDARY
    keep = [
        "AuditID",
        "RouteID",
        "GridIndex",
        "z_grid",
        "DepthZone",
        "SignStable",
        "WhitenedTarget",
        "K1Whitened",
        "K2LockedWhitened",
        "SmokeBackreactionWhitened",
        "RegularizedNullChi2Contribution",
        "K1Chi2Contribution",
        "K2Chi2Contribution",
        "DeltaChi2_K2_minus_RegularizedNull_Row",
        "DeltaChi2_K2_minus_K1_Row",
        "DominanceClass",
        "K2BeatsRegularizedNullRow",
        "K2BeatsK1Row",
        "RegularizedNullBeatsK2Row",
        "SignMatchesTarget",
        "SignMatchesK2",
        "MeasurementValidationAllowed",
        "ClaimBoundary",
    ]
    out[keep].to_csv(OUT_ROW, index=False)

    zone_rows = []
    for (route_id, zone), g in out.groupby(["RouteID", "DepthZone"], sort=False):
        zone_rows.append(
            {
                "AuditID": "REGULARIZED_200_NULL_DOMINANCE_ZONE_AUDIT_V1",
                "RouteID": route_id,
                "DepthZone": zone,
                "Rows": int(len(g)),
                "StableRows": int(g["SignStable"].astype(bool).sum()),
                "RegularizedNullChi2": float(g["RegularizedNullChi2Contribution"].sum()),
                "K1Chi2": float(g["K1Chi2Contribution"].sum()),
                "K2Chi2": float(g["K2Chi2Contribution"].sum()),
                "DeltaChi2_K2_minus_RegularizedNull": float(
                    g["K2Chi2Contribution"].sum() - g["RegularizedNullChi2Contribution"].sum()
                ),
                "DeltaChi2_K2_minus_K1": float(g["K2Chi2Contribution"].sum() - g["K1Chi2Contribution"].sum()),
                "K2BeatsRegularizedNullRows": int(g["K2BeatsRegularizedNullRow"].sum()),
                "K2BeatsK1Rows": int(g["K2BeatsK1Row"].sum()),
                "RegularizedNullBeatsK2Rows": int(g["RegularizedNullBeatsK2Row"].sum()),
                "DominanceStatus": "K2_ZONE_BETTER_THAN_REGULARIZED_NULL"
                if g["K2Chi2Contribution"].sum() < g["RegularizedNullChi2Contribution"].sum()
                else "REGULARIZED_NULL_ZONE_BETTER_THAN_K2",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    zone = pd.DataFrame(zone_rows)
    zone.to_csv(OUT_ZONE, index=False)

    k2_route_wins = int((score["DeltaChi2_K2_minus_SmokeBackreaction"] < 0.0).sum())
    route_count = int(score["RouteID"].nunique())
    row_count = int(len(out))
    k2_row_wins = int(out["K2BeatsRegularizedNullRow"].sum())
    null_row_wins = int(out["RegularizedNullBeatsK2Row"].sum())
    k2_zone_wins = int(zone["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_REGULARIZED_NULL").sum())
    zone_count = int(len(zone))
    stable = out[out["SignStable"].astype(bool)]
    stable_k2_row_wins = int(stable["K2BeatsRegularizedNullRow"].sum())
    stable_null_row_wins = int(stable["RegularizedNullBeatsK2Row"].sum())
    low = zone[zone["DepthZone"].eq("low_depth")]
    midhigh = zone[~zone["DepthZone"].eq("low_depth")]

    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGULARIZED_200_NULL_DOMINANCE_AUDIT_V1",
                "RoutesScored": route_count,
                "K2BeatsRegularizedNullRoutes": k2_route_wins,
                "Rows": row_count,
                "K2BeatsRegularizedNullRows": k2_row_wins,
                "RegularizedNullBeatsK2Rows": null_row_wins,
                "StableRows": int(len(stable)),
                "StableK2BeatsRegularizedNullRows": stable_k2_row_wins,
                "StableRegularizedNullBeatsK2Rows": stable_null_row_wins,
                "Zones": zone_count,
                "K2BeatsRegularizedNullZones": k2_zone_wins,
                "LowDepthZonesK2Better": int(low["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_REGULARIZED_NULL").sum()),
                "MidHighZonesK2Better": int(midhigh["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_REGULARIZED_NULL").sum()),
                "MedianDeltaChi2_K2_minus_RegularizedNull_Route": float(
                    score["DeltaChi2_K2_minus_SmokeBackreaction"].median()
                ),
                "MedianCorrelationNullWithK2": float(score["CorrelationWithK2"].median()),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "K2_DOMINATES_REGULARIZED_200_NULL_PREFLIGHT"
                if k2_route_wins == route_count and k2_zone_wins == zone_count
                else "REGULARIZED_200_NULL_HAS_LOCAL_ADVANTAGES",
                "StrongestAllowedClaim": (
                    "locked K2 remains more competitive than the regularized 200-bootstrap backreaction null in the current preflight benchmark"
                ),
                "PrimaryResidualRisk": (
                    "row-level target construction and source-native covariance remain required before measurement validation"
                ),
                "NextAction": (
                    "move to source-native covariance and upstream D_A,H_D derivative table acquisition"
                ),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Regularized 200 Null Dominance Audit",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This audit decomposes the regularized 200-bootstrap backreaction null against locked K2 by row and depth zone. It does not modify K2, refit K1, allow a scale fit, or authorize measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- K2 beats regularized null routes: {k2_route_wins}/{route_count}",
                f"- K2 beats regularized null rows: {k2_row_wins}/{row_count}",
                f"- K2 beats regularized null zones: {k2_zone_wins}/{zone_count}",
                f"- Stable rows K2 beats regularized null: {stable_k2_row_wins}/{len(stable)}",
                f"- Median route DeltaChi2 K2-null: {float(score['DeltaChi2_K2_minus_SmokeBackreaction'].median())}",
                "",
                "## Boundary",
                "",
                "This is a preflight dominance audit only. It is not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_ROW.relative_to(ROOT)}")
    print(f"Wrote {OUT_ZONE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
