#!/usr/bin/env python3
"""Diagnose why provisional backreaction resembles K2 but not the target."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROW_AUDIT = EVIDENCE / "provisional_backreaction_preflight_row_audit.csv"
SUMMARY = EVIDENCE / "provisional_backreaction_preflight_summary.csv"

OUT_ROW = EVIDENCE / "provisional_backreaction_bridge_diagnosis_row.csv"
OUT_ZONE = EVIDENCE / "provisional_backreaction_bridge_diagnosis_zone.csv"
OUT_SUMMARY = EVIDENCE / "provisional_backreaction_bridge_diagnosis_summary.csv"
OUT_DOC = DOCS / "provisional_backreaction_bridge_diagnosis.md"


def depth_zone(z: float) -> str:
    if z < 0.9:
        return "low_depth"
    if z < 1.6:
        return "mid_depth"
    return "high_depth"


def chi2(residual: np.ndarray) -> float:
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def best_scale(y: np.ndarray, x: np.ndarray) -> float:
    denom = float(x @ x)
    if denom <= 0.0:
        return float("nan")
    return float((x @ y) / denom)


def sign_match_count(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.sum(np.sign(a) == np.sign(b)))


def classify(row: pd.Series) -> str:
    if bool(row["RawSignMatchesK2"]) and not bool(row["RawSignMatchesTarget"]):
        return "K2_ALIGNED_TARGET_ANTI_ALIGNED"
    if bool(row["RawSignMatchesK2"]) and bool(row["RawSignMatchesTarget"]):
        return "K2_AND_TARGET_ALIGNED"
    if not bool(row["RawSignMatchesK2"]) and bool(row["RawSignMatchesTarget"]):
        return "TARGET_ALIGNED_K2_ANTI_ALIGNED"
    return "BOTH_ANTI_ALIGNED_OR_NEAR_ZERO"


def summarize_subset(route_id: str, subset_id: str, df: pd.DataFrame) -> dict[str, object]:
    target = df["WhitenedTarget"].to_numpy(float)
    k2 = df["K2LockedWhitened"].to_numpy(float)
    br = df["BackreactionRawWhitened"].to_numpy(float)
    br_inv = -br
    stable = df["SignStable"].astype(bool).to_numpy()
    stable_df = df[stable]

    return {
        "DiagnosisID": "PROVISIONAL_BACKREACTION_BRIDGE_DIAGNOSIS_V1",
        "RouteID": route_id,
        "SubsetID": subset_id,
        "Rows": len(df),
        "StableRows": int(np.sum(stable)),
        "BackreactionChi2ToTarget": chi2(target - br),
        "InvertedBackreactionChi2ToTargetForbidden": chi2(target - br_inv),
        "K2Chi2ToTarget": chi2(target - k2),
        "BackreactionChi2ToK2": chi2(k2 - br),
        "CorrelationBackreactionTarget": corr(br, target),
        "CorrelationBackreactionK2": corr(br, k2),
        "CorrelationInvertedBackreactionTargetForbidden": corr(br_inv, target),
        "SignMatchesTarget": sign_match_count(br, target),
        "SignMatchesK2": sign_match_count(br, k2),
        "StableSignMatchesTarget": sign_match_count(stable_df["BackreactionRawWhitened"].to_numpy(float), stable_df["WhitenedTarget"].to_numpy(float)) if len(stable_df) else 0,
        "StableSignMatchesK2": sign_match_count(stable_df["BackreactionRawWhitened"].to_numpy(float), stable_df["K2LockedWhitened"].to_numpy(float)) if len(stable_df) else 0,
        "ForbiddenScaleToTarget": best_scale(target, br),
        "ForbiddenScaleToK2": best_scale(k2, br),
        "ScaleFitAllowed": False,
        "MeasurementValidationAllowed": False,
        "ClaimBoundary": "provisional_backreaction_bridge_diagnosis_no_measurement_validation",
    }


def main() -> None:
    row = pd.read_csv(ROW_AUDIT)
    summary = pd.read_csv(SUMMARY)

    row["DepthZone"] = row["z_grid"].map(depth_zone)
    row["BridgeTensionClass"] = row.apply(classify, axis=1)
    row["AbsResidualToTarget"] = row["BackreactionRawResidualToTarget"].abs()
    row["AbsResidualToK2"] = row["BackreactionRawResidualToK2"].abs()
    row["K2CloserThanBackreactionToTarget"] = (
        (row["WhitenedTarget"] - row["K2LockedWhitened"]).abs() < row["AbsResidualToTarget"]
    )
    row["BackreactionCloserThanK1ToTarget"] = (
        row["AbsResidualToTarget"] < (row["WhitenedTarget"] - row["K1Whitened"]).abs()
    )
    row["InvertedBackreactionResidualToTargetForbidden"] = row["WhitenedTarget"] + row["BackreactionRawWhitened"]
    row["ClaimBoundary"] = "provisional_backreaction_bridge_diagnosis_no_measurement_validation"
    row.to_csv(OUT_ROW, index=False)

    zone_rows = []
    for route_id, group in row.groupby("RouteID", sort=True):
        zone_rows.append(summarize_subset(route_id, "all_depth", group))
        zone_rows.append(summarize_subset(route_id, "mid_high_depth", group[group["DepthZone"].ne("low_depth")]))
        for zone, zone_group in group.groupby("DepthZone", sort=True):
            zone_rows.append(summarize_subset(route_id, zone, zone_group))
    zone = pd.DataFrame(zone_rows)
    zone.to_csv(OUT_ZONE, index=False)

    total_rows = len(row)
    k2_aligned_target_anti = int(row["BridgeTensionClass"].eq("K2_ALIGNED_TARGET_ANTI_ALIGNED").sum())
    both_aligned = int(row["BridgeTensionClass"].eq("K2_AND_TARGET_ALIGNED").sum())
    k2_closer = int(row["K2CloserThanBackreactionToTarget"].sum())
    br_closer_than_k1 = int(row["BackreactionCloserThanK1ToTarget"].sum())
    route_status = ";".join(
        f"{r.RouteID}:{r.CurrentStatus}" for r in summary.itertuples(index=False)
    )
    overall = pd.DataFrame(
        [
            {
                "DiagnosisID": "PROVISIONAL_BACKREACTION_BRIDGE_DIAGNOSIS_V1",
                "Routes": row["RouteID"].nunique(),
                "Rows": total_rows,
                "K2AlignedTargetAntiAlignedRows": k2_aligned_target_anti,
                "K2AndTargetAlignedRows": both_aligned,
                "RowsWhereK2CloserThanBackreactionToTarget": k2_closer,
                "RowsWhereBackreactionCloserThanK1ToTarget": br_closer_than_k1,
                "RouteStatuses": route_status,
                "CurrentStatus": "BRIDGE_SIGN_OR_OBSERVABLE_MISMATCH_DOMINATES_PROVISIONAL_BACKREACTION",
                "StrongestAllowedClaim": (
                    "the provisional BAO-only backreaction bridge has K2-like shape components but fails the target-space sign/observable bridge"
                ),
                "PrimaryResidualRisk": "source-native symbolic-regression reconstruction and observable mapping are still missing",
                "NextAction": "test source-native reconstruction or explicitly derive an observable bridge before treating backreaction as a fair null",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "provisional_backreaction_bridge_diagnosis_no_measurement_validation",
            }
        ]
    )
    overall.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Provisional Backreaction Bridge Diagnosis",
        "",
        "Status: bridge mismatch diagnosed; no measurement-validation claim.",
        "",
        "The provisional BAO-only backreaction curve is K2-like in parts, but it is not aligned with the target-space branch contrast. The dominant issue is not merely amplitude: sign and observable mapping are also involved.",
        "",
        "## Outputs",
        "",
        f"- Row diagnosis: `{OUT_ROW.relative_to(ROOT)}`",
        f"- Zone diagnosis: `{OUT_ZONE.relative_to(ROOT)}`",
        f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
        "",
        "## Claim Boundary",
        "",
        "Fitted scale and inverted-sign diagnostics are forbidden for claims. They only identify whether the problem is amplitude, sign, or observable bridge.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_ZONE}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
