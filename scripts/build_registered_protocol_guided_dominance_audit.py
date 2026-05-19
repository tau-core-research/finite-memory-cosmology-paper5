#!/usr/bin/env python3
"""Row and zone dominance audit for registered-protocol-guided families."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW = EVIDENCE / "registered_protocol_guided_bridge_row_audit.csv"
SCORE = EVIDENCE / "registered_protocol_guided_bridge_scorecard.csv"

OUT_ROW = EVIDENCE / "registered_protocol_guided_dominance_row_audit.csv"
OUT_ZONE = EVIDENCE / "registered_protocol_guided_dominance_zone_audit.csv"
OUT_SUMMARY = EVIDENCE / "registered_protocol_guided_dominance_summary.csv"
OUT_DOC = DOCS / "registered_protocol_guided_dominance_audit.md"

CLAIM_BOUNDARY = "registered_protocol_guided_dominance_no_measurement_validation"


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
    out.to_csv(OUT_ROW, index=False)

    zone_rows = []
    for (route_id, family_id, zone), group in out.groupby(["RouteID", "FamilyID", "DepthZone"], sort=False):
        family_chi2 = float(group["FamilyChi2Contribution"].sum())
        k1_chi2 = float(group["K1Chi2Contribution"].sum())
        k2_chi2 = float(group["K2Chi2Contribution"].sum())
        zone_rows.append(
            {
                "AuditID": "REGISTERED_PROTOCOL_GUIDED_DOMINANCE_ZONE_AUDIT_V1",
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
    stable = out[out["SignStable"].astype(bool)]
    summary = pd.DataFrame(
        [
            {
                "AuditID": "REGISTERED_PROTOCOL_GUIDED_DOMINANCE_AUDIT_V1",
                "FamiliesScored": int(score["FamilyID"].nunique()),
                "RoutesScored": int(score["RouteID"].nunique()),
                "RouteFamilyCases": route_family_cases,
                "K2BeatsFamilyRouteCases": k2_route_family_wins,
                "Rows": int(len(out)),
                "K2BeatsFamilyRows": int(out["K2BeatsFamilyRow"].sum()),
                "FamilyBeatsK2Rows": int(out["FamilyBeatsK2Row"].sum()),
                "StableRows": int(len(stable)),
                "StableK2BeatsFamilyRows": int(stable["K2BeatsFamilyRow"].sum()),
                "StableFamilyBeatsK2Rows": int(stable["FamilyBeatsK2Row"].sum()),
                "Zones": int(len(zone)),
                "K2BeatsFamilyZones": int(zone["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()),
                "MedianDeltaChi2_K2_minus_Family_Route": float(
                    score["DeltaChi2_K2_minus_FamilyBackreaction"].median()
                ),
                "MedianCorrelationFamilyWithK2": float(score["CorrelationFamilyWithK2"].median()),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "SourceExport": False,
                "SourceNative": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "K2_DOMINATES_REGISTERED_PROTOCOL_GUIDED_FAMILIES_PREFLIGHT"
                if k2_route_family_wins == route_family_cases
                and int(zone["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_FAMILY").sum()) == len(zone)
                else "REGISTERED_PROTOCOL_GUIDED_FAMILIES_HAVE_LOCAL_ADVANTAGES",
                "StrongestAllowedClaim": (
                    "locked K2 remains more competitive than the registered-protocol-guided local families in the current preflight benchmark"
                ),
                "PrimaryResidualRisk": (
                    "manual protocol-selection details and branch-specific DESI/eBOSS exports remain unavailable"
                ),
                "NextAction": "implement DESI/eBOSS branch-specific reproductions and keep fully source-native gate closed",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Registered-Protocol-Guided Dominance Audit",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This audit decomposes publication-protocol-guided local families against locked K2 by row and depth zone. It does not modify K2, refit K1, allow a scale fit, or authorize measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- K2 beats route-family cases: {k2_route_family_wins}/{route_family_cases}",
                f"- K2 beats rows: {int(out['K2BeatsFamilyRow'].sum())}/{len(out)}",
                f"- K2 beats zones: {int(zone['DominanceStatus'].eq('K2_ZONE_BETTER_THAN_FAMILY').sum())}/{len(zone)}",
                f"- Stable rows K2 beats family: {int(stable['K2BeatsFamilyRow'].sum())}/{len(stable)}",
                f"- Median route DeltaChi2 K2-family: {float(score['DeltaChi2_K2_minus_FamilyBackreaction'].median())}",
                "",
                "## Boundary",
                "",
                "This is not source-native validation.",
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
