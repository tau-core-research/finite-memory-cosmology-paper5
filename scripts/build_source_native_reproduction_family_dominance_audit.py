#!/usr/bin/env python3
"""Row and zone dominance audit for local reproduction families."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW = EVIDENCE / "source_native_reproduction_family_bridge_row_audit.csv"
SCORE = EVIDENCE / "source_native_reproduction_family_bridge_scorecard.csv"

OUT_ROW = EVIDENCE / "source_native_reproduction_family_dominance_row_audit.csv"
OUT_ZONE = EVIDENCE / "source_native_reproduction_family_dominance_zone_audit.csv"
OUT_SUMMARY = EVIDENCE / "source_native_reproduction_family_dominance_summary.csv"
OUT_DOC = DOCS / "source_native_reproduction_family_dominance_audit.md"

CLAIM_BOUNDARY = "source_native_reproduction_family_dominance_no_measurement_validation"


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
        "Family": float(row["FamilyChi2Contribution"]),
    }
    winner = min(values, key=values.get)
    if winner == "K2":
        return "K2_LOWEST_ROW_CHI2"
    if winner == "K1":
        return "K1_LOWEST_ROW_CHI2"
    return "FAMILY_LOWEST_ROW_CHI2"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    row = pd.read_csv(ROW)
    score = pd.read_csv(SCORE)
    out = row.copy()
    out["DepthZone"] = out["z_grid"].map(depth_zone)
    out["FamilyChi2Contribution"] = (out["WhitenedTarget"] - out["FamilyBackreactionWhitened"]) ** 2
    out["K1Chi2Contribution"] = (out["WhitenedTarget"] - out["K1Whitened"]) ** 2
    out["K2Chi2Contribution"] = (out["WhitenedTarget"] - out["K2LockedWhitened"]) ** 2
    out["DeltaChi2_K2_minus_Family_Row"] = out["K2Chi2Contribution"] - out["FamilyChi2Contribution"]
    out["DeltaChi2_K2_minus_K1_Row"] = out["K2Chi2Contribution"] - out["K1Chi2Contribution"]
    out["DominanceClass"] = out.apply(classify, axis=1)
    out["K2BeatsFamilyRow"] = out["K2Chi2Contribution"] < out["FamilyChi2Contribution"]
    out["K2BeatsK1Row"] = out["K2Chi2Contribution"] < out["K1Chi2Contribution"]
    out["FamilyBeatsK2Row"] = out["FamilyChi2Contribution"] < out["K2Chi2Contribution"]
    out["MeasurementValidationAllowed"] = False
    out["ClaimBoundary"] = CLAIM_BOUNDARY
    keep = [
        "AuditID",
        "RouteID",
        "FamilyID",
        "GridIndex",
        "z_grid",
        "DepthZone",
        "SignStable",
        "WhitenedTarget",
        "K1Whitened",
        "K2LockedWhitened",
        "FamilyBackreactionWhitened",
        "FamilyChi2Contribution",
        "K1Chi2Contribution",
        "K2Chi2Contribution",
        "DeltaChi2_K2_minus_Family_Row",
        "DeltaChi2_K2_minus_K1_Row",
        "DominanceClass",
        "K2BeatsFamilyRow",
        "K2BeatsK1Row",
        "FamilyBeatsK2Row",
        "SignMatchesTarget",
        "SignMatchesK2",
        "MeasurementValidationAllowed",
        "ClaimBoundary",
    ]
    out[keep].to_csv(OUT_ROW, index=False)

    zone_rows = []
    for (route_id, family_id, zone), group in out.groupby(["RouteID", "FamilyID", "DepthZone"], sort=False):
        family_chi2 = float(group["FamilyChi2Contribution"].sum())
        k1_chi2 = float(group["K1Chi2Contribution"].sum())
        k2_chi2 = float(group["K2Chi2Contribution"].sum())
        zone_rows.append(
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_FAMILY_DOMINANCE_ZONE_AUDIT_V1",
                "RouteID": route_id,
                "FamilyID": family_id,
                "DepthZone": zone,
                "Rows": int(len(group)),
                "StableRows": int(group["SignStable"].astype(bool).sum()),
                "FamilyChi2": family_chi2,
                "K1Chi2": k1_chi2,
                "K2Chi2": k2_chi2,
                "DeltaChi2_K2_minus_Family": k2_chi2 - family_chi2,
                "DeltaChi2_K2_minus_K1": k2_chi2 - k1_chi2,
                "K2BeatsFamilyRows": int(group["K2BeatsFamilyRow"].sum()),
                "K2BeatsK1Rows": int(group["K2BeatsK1Row"].sum()),
                "FamilyBeatsK2Rows": int(group["FamilyBeatsK2Row"].sum()),
                "DominanceStatus": "K2_ZONE_BETTER_THAN_FAMILY"
                if k2_chi2 < family_chi2
                else "FAMILY_ZONE_BETTER_THAN_K2",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    zone = pd.DataFrame(zone_rows)
    zone.to_csv(OUT_ZONE, index=False)

    route_family_cases = len(score)
    k2_route_family_wins = int((score["DeltaChi2_K2_minus_FamilyBackreaction"] < 0.0).sum())
    row_count = len(out)
    zone_count = len(zone)
    stable = out[out["SignStable"].astype(bool)]
    low = zone[zone["DepthZone"].eq("low_depth")]
    midhigh = zone[~zone["DepthZone"].eq("low_depth")]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_FAMILY_DOMINANCE_AUDIT_V1",
                "FamiliesScored": int(score["FamilyID"].nunique()),
                "RoutesScored": int(score["RouteID"].nunique()),
                "RouteFamilyCases": route_family_cases,
                "K2BeatsFamilyRouteCases": k2_route_family_wins,
                "Rows": row_count,
                "K2BeatsFamilyRows": int(out["K2BeatsFamilyRow"].sum()),
                "FamilyBeatsK2Rows": int(out["FamilyBeatsK2Row"].sum()),
                "StableRows": int(len(stable)),
                "StableK2BeatsFamilyRows": int(stable["K2BeatsFamilyRow"].sum()),
                "StableFamilyBeatsK2Rows": int(stable["FamilyBeatsK2Row"].sum()),
                "Zones": zone_count,
                "K2BeatsFamilyZones": int(zone["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()),
                "LowDepthZonesK2Better": int(low["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()),
                "MidHighZonesK2Better": int(midhigh["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()),
                "MedianDeltaChi2_K2_minus_Family_Route": float(
                    score["DeltaChi2_K2_minus_FamilyBackreaction"].median()
                ),
                "MedianCorrelationFamilyWithK2": float(score["CorrelationFamilyWithK2"].median()),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "AuthorExport": False,
                "ReproductionFamily": True,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "K2_DOMINATES_LOCAL_REPRODUCTION_FAMILIES_PREFLIGHT"
                if k2_route_family_wins == route_family_cases
                and int(zone["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()) == zone_count
                else "LOCAL_REPRODUCTION_FAMILIES_HAVE_LOCAL_ADVANTAGES",
                "StrongestAllowedClaim": (
                    "locked K2 remains more competitive than all local reproduction families in the current preflight benchmark"
                ),
                "PrimaryResidualRisk": (
                    "local family rules are not author/source-native symbolic-regression exports"
                ),
                "NextAction": "stress-test the local family rules and then use the same scorer for author/source-native exports if they become available",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Reproduction Family Dominance Audit",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This audit decomposes local reproduction families against locked K2 by row and depth zone. It does not modify K2, refit K1, allow a scale fit, or authorize measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- K2 beats route-family cases: {k2_route_family_wins}/{route_family_cases}",
                f"- K2 beats family rows: {int(out['K2BeatsFamilyRow'].sum())}/{row_count}",
                f"- K2 beats family zones: {int(zone['DominanceStatus'].eq('K2_ZONE_BETTER_THAN_FAMILY').sum())}/{zone_count}",
                f"- Stable rows K2 beats family: {int(stable['K2BeatsFamilyRow'].sum())}/{len(stable)}",
                f"- Median route DeltaChi2 K2-family: {float(score['DeltaChi2_K2_minus_FamilyBackreaction'].median())}",
                "",
                "## Boundary",
                "",
                "This is a local reproduction-family preflight audit only. It is not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_SUMMARY.relative_to(ROOT)}")
    print(f"Wrote {OUT_ROW.relative_to(ROOT)}")
    print(f"Wrote {OUT_ZONE.relative_to(ROOT)}")
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
