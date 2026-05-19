#!/usr/bin/env python3
"""Row and zone dominance audit for the reproduction-candidate null."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW = EVIDENCE / "source_native_reproduction_candidate_bridge_row_audit.csv"
SCORE = EVIDENCE / "source_native_reproduction_candidate_bridge_scorecard.csv"

OUT_ROW = EVIDENCE / "source_native_reproduction_candidate_dominance_row_audit.csv"
OUT_ZONE = EVIDENCE / "source_native_reproduction_candidate_dominance_zone_audit.csv"
OUT_SUMMARY = EVIDENCE / "source_native_reproduction_candidate_dominance_summary.csv"
OUT_DOC = DOCS / "source_native_reproduction_candidate_dominance_audit.md"

CLAIM_BOUNDARY = "source_native_reproduction_candidate_dominance_no_measurement_validation"


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
        "Candidate": float(row["CandidateChi2Contribution"]),
    }
    winner = min(values, key=values.get)
    if winner == "K2":
        return "K2_LOWEST_ROW_CHI2"
    if winner == "K1":
        return "K1_LOWEST_ROW_CHI2"
    return "CANDIDATE_LOWEST_ROW_CHI2"


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    row = pd.read_csv(ROW)
    score = pd.read_csv(SCORE)
    out = row.copy()
    out["DepthZone"] = out["z_grid"].map(depth_zone)
    out["CandidateChi2Contribution"] = (out["WhitenedTarget"] - out["CandidateBackreactionWhitened"]) ** 2
    out["K1Chi2Contribution"] = (out["WhitenedTarget"] - out["K1Whitened"]) ** 2
    out["K2Chi2Contribution"] = (out["WhitenedTarget"] - out["K2LockedWhitened"]) ** 2
    out["DeltaChi2_K2_minus_Candidate_Row"] = out["K2Chi2Contribution"] - out["CandidateChi2Contribution"]
    out["DeltaChi2_K2_minus_K1_Row"] = out["K2Chi2Contribution"] - out["K1Chi2Contribution"]
    out["DominanceClass"] = out.apply(classify, axis=1)
    out["K2BeatsCandidateRow"] = out["K2Chi2Contribution"] < out["CandidateChi2Contribution"]
    out["K2BeatsK1Row"] = out["K2Chi2Contribution"] < out["K1Chi2Contribution"]
    out["CandidateBeatsK2Row"] = out["CandidateChi2Contribution"] < out["K2Chi2Contribution"]
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
        "CandidateBackreactionWhitened",
        "CandidateChi2Contribution",
        "K1Chi2Contribution",
        "K2Chi2Contribution",
        "DeltaChi2_K2_minus_Candidate_Row",
        "DeltaChi2_K2_minus_K1_Row",
        "DominanceClass",
        "K2BeatsCandidateRow",
        "K2BeatsK1Row",
        "CandidateBeatsK2Row",
        "SignMatchesTarget",
        "SignMatchesK2",
        "MeasurementValidationAllowed",
        "ClaimBoundary",
    ]
    out[keep].to_csv(OUT_ROW, index=False)

    zone_rows = []
    for (route_id, zone), group in out.groupby(["RouteID", "DepthZone"], sort=False):
        candidate_chi2 = float(group["CandidateChi2Contribution"].sum())
        k1_chi2 = float(group["K1Chi2Contribution"].sum())
        k2_chi2 = float(group["K2Chi2Contribution"].sum())
        zone_rows.append(
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_DOMINANCE_ZONE_AUDIT_V1",
                "RouteID": route_id,
                "DepthZone": zone,
                "Rows": int(len(group)),
                "StableRows": int(group["SignStable"].astype(bool).sum()),
                "CandidateChi2": candidate_chi2,
                "K1Chi2": k1_chi2,
                "K2Chi2": k2_chi2,
                "DeltaChi2_K2_minus_Candidate": k2_chi2 - candidate_chi2,
                "DeltaChi2_K2_minus_K1": k2_chi2 - k1_chi2,
                "K2BeatsCandidateRows": int(group["K2BeatsCandidateRow"].sum()),
                "K2BeatsK1Rows": int(group["K2BeatsK1Row"].sum()),
                "CandidateBeatsK2Rows": int(group["CandidateBeatsK2Row"].sum()),
                "DominanceStatus": "K2_ZONE_BETTER_THAN_CANDIDATE"
                if k2_chi2 < candidate_chi2
                else "CANDIDATE_ZONE_BETTER_THAN_K2",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    zone_df = pd.DataFrame(zone_rows)
    zone_df.to_csv(OUT_ZONE, index=False)

    route_count = int(score["RouteID"].nunique())
    k2_route_wins = int((score["DeltaChi2_K2_minus_CandidateBackreaction"] < 0.0).sum())
    row_count = int(len(out))
    k2_row_wins = int(out["K2BeatsCandidateRow"].sum())
    candidate_row_wins = int(out["CandidateBeatsK2Row"].sum())
    stable = out[out["SignStable"].astype(bool)]
    zone_count = int(len(zone_df))
    k2_zone_wins = int(zone_df["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_CANDIDATE").sum())
    low = zone_df[zone_df["DepthZone"].eq("low_depth")]
    midhigh = zone_df[~zone_df["DepthZone"].eq("low_depth")]

    summary = pd.DataFrame(
        [
            {
                "AuditID": "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_DOMINANCE_AUDIT_V1",
                "RoutesScored": route_count,
                "K2BeatsCandidateRoutes": k2_route_wins,
                "Rows": row_count,
                "K2BeatsCandidateRows": k2_row_wins,
                "CandidateBeatsK2Rows": candidate_row_wins,
                "StableRows": int(len(stable)),
                "StableK2BeatsCandidateRows": int(stable["K2BeatsCandidateRow"].sum()),
                "StableCandidateBeatsK2Rows": int(stable["CandidateBeatsK2Row"].sum()),
                "Zones": zone_count,
                "K2BeatsCandidateZones": k2_zone_wins,
                "LowDepthZonesK2Better": int(low["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_CANDIDATE").sum()),
                "MidHighZonesK2Better": int(midhigh["DominanceStatus"].eq("K2_ZONE_BETTER_THAN_CANDIDATE").sum()),
                "MedianDeltaChi2_K2_minus_Candidate_Route": float(
                    score["DeltaChi2_K2_minus_CandidateBackreaction"].median()
                ),
                "MedianCorrelationCandidateWithK2": float(score["CorrelationCandidateWithK2"].median()),
                "K2KernelChanged": False,
                "K1Refit": False,
                "ScaleFitAllowed": False,
                "AuthorExport": False,
                "ReproductionCandidate": True,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "K2_DOMINATES_REPRODUCTION_CANDIDATE_PREFLIGHT"
                if k2_route_wins == route_count and k2_zone_wins == zone_count
                else "REPRODUCTION_CANDIDATE_HAS_LOCAL_ADVANTAGES",
                "StrongestAllowedClaim": (
                    "locked K2 remains more competitive than the local reproduction candidate in the current preflight benchmark"
                ),
                "PrimaryResidualRisk": (
                    "the candidate is not the author derivative export and source-native validation remains blocked"
                ),
                "NextAction": "obtain author/source-native derivative exports and covariance, then rerun this audit unchanged",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        "\n".join(
            [
                "# Source-Native Reproduction Candidate Dominance Audit",
                "",
                f"Status: {summary.iloc[0]['CurrentStatus']}.",
                "",
                "This audit decomposes the local reproduction candidate against locked K2 by row and depth zone. It does not modify K2, refit K1, allow a scale fit, or authorize measurement validation.",
                "",
                "## Key Numbers",
                "",
                f"- K2 beats candidate routes: {k2_route_wins}/{route_count}",
                f"- K2 beats candidate rows: {k2_row_wins}/{row_count}",
                f"- K2 beats candidate zones: {k2_zone_wins}/{zone_count}",
                f"- Stable rows K2 beats candidate: {int(stable['K2BeatsCandidateRow'].sum())}/{len(stable)}",
                f"- Median route DeltaChi2 K2-candidate: {float(score['DeltaChi2_K2_minus_CandidateBackreaction'].median())}",
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
    print(f"Wrote {OUT_DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
