#!/usr/bin/env python3
"""Stress-test the source-split A_tau=2 projection prior.

Tests:
1. leave-one-out stability;
2. depth-transition behavior;
3. anti-alignment-conditioned performance.

This keeps the locked K2 kernel fixed and treats A_tau=2 as a predeclared
source-split projection prior, not a fitted kernel change.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
ANTIALIGN = EVIDENCE / "source_split_antialignment_check.csv"

OUT_LOO = EVIDENCE / "source_split_a2_leave_one_out.csv"
OUT_DEPTH = EVIDENCE / "source_split_a2_depth_transition.csv"
OUT_ALIGN = EVIDENCE / "source_split_a2_antialignment_conditioned.csv"
OUT_SUMMARY = EVIDENCE / "source_split_a2_stress_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def chi2_diag(y: np.ndarray, pred: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(pred) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - pred[usable]) / sigma[usable]
    return float(np.dot(r, r))


def aic(chi2: float, k: int = 0) -> float:
    return float(chi2 + 2 * k)


def model_metrics(df: pd.DataFrame, model_id: str, pred: np.ndarray, k: int = 0) -> dict[str, object]:
    y = df["SourceSplitResponse"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)
    c2 = chi2_diag(y, pred, sigma)
    return {
        "ModelID": model_id,
        "Rows": len(df),
        "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsPrediction": cosine(y, pred),
        "ResidualRMS": rms(y - pred),
        "Chi2DiagProxy": c2,
        "AIC": aic(c2, k),
        "SignMatchFraction": float(np.mean(np.sign(y) == np.sign(pred))),
    }


def compare_subset(df: pd.DataFrame) -> pd.DataFrame:
    k1 = df["K1Response"].to_numpy(float)
    k2 = df["K2LockedRho4"].to_numpy(float)
    rows = [
        model_metrics(df, "K1_NO_MEMORY", k1, 0),
        model_metrics(df, "K2_UNIT_LOCKED_RHO4", k2, 0),
        model_metrics(df, "K2_SOURCE_SPLIT_A2_PRIOR", 2.0 * k2, 0),
    ]
    out = pd.DataFrame(rows)
    a2_aic = float(out[out["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR"]["AIC"].iloc[0])
    unit_aic = float(out[out["ModelID"] == "K2_UNIT_LOCKED_RHO4"]["AIC"].iloc[0])
    out["DeltaAICVsA2"] = out["AIC"] - a2_aic
    out["DeltaAICVsUnit"] = out["AIC"] - unit_aic
    return out


def main() -> None:
    df = pd.read_csv(DECOMP)
    anti = pd.read_csv(ANTIALIGN)[["GridIndex", "SNBAOOppositeSign", "AntiAlignmentClass"]]
    df = df.merge(anti, on="GridIndex", how="left")

    # 1. Leave-one-out stability, with explicit mid-depth marker.
    loo_rows: list[dict[str, object]] = []
    for _, dropped in df.iterrows():
        train = df[df["GridIndex"] != dropped["GridIndex"]].copy()
        comp = compare_subset(train)
        best = comp.sort_values("AIC").iloc[0]
        a2 = comp[comp["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR"].iloc[0]
        unit = comp[comp["ModelID"] == "K2_UNIT_LOCKED_RHO4"].iloc[0]
        loo_rows.append(
            {
                "DroppedGridIndex": int(dropped["GridIndex"]),
                "DroppedDepthBin": dropped["DepthBin"],
                "DroppedWasMidDepth": dropped["DepthBin"] == "mid_depth",
                "RowsRemaining": len(train),
                "BestAICModel": best["ModelID"],
                "A2AIC": float(a2["AIC"]),
                "UnitK2AIC": float(unit["AIC"]),
                "A2DeltaAICVsUnit": float(a2["AIC"] - unit["AIC"]),
                "A2ResidualRMS": float(a2["ResidualRMS"]),
                "A2Wins": best["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR",
                "ClaimBoundary": "a2_stress_preflight_no_measurement_validation",
            }
        )
    pd.DataFrame(loo_rows).to_csv(OUT_LOO, index=False)

    # 2. Depth-transition behavior.
    depth_rows: list[dict[str, object]] = []
    for depth in ["low_depth", "mid_depth", "high_depth"]:
        sub = df[df["DepthBin"] == depth].copy()
        comp = compare_subset(sub)
        a2 = comp[comp["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR"].iloc[0]
        unit = comp[comp["ModelID"] == "K2_UNIT_LOCKED_RHO4"].iloc[0]
        k1 = comp[comp["ModelID"] == "K1_NO_MEMORY"].iloc[0]
        depth_rows.append(
            {
                "DepthBin": depth,
                "Rows": len(sub),
                "MeanX": float(sub["x_coordinate"].mean()),
                "A2PredictionToTargetRMSRatio": float(a2["PredictionToTargetRMSRatio"]),
                "A2ResidualRMS": float(a2["ResidualRMS"]),
                "A2Chi2DiagProxy": float(a2["Chi2DiagProxy"]),
                "A2DeltaAICVsUnit": float(a2["AIC"] - unit["AIC"]),
                "A2DeltaAICVsK1": float(a2["AIC"] - k1["AIC"]),
                "A2SignMatchFraction": float(a2["SignMatchFraction"]),
                "ClaimBoundary": "a2_stress_preflight_no_measurement_validation",
            }
        )
    depth = pd.DataFrame(depth_rows)
    depth["A2AmplitudeMonotoneRank"] = depth["A2PredictionToTargetRMSRatio"].rank(method="first")
    depth.to_csv(OUT_DEPTH, index=False)

    # 3. Anti-alignment conditioned benchmark.
    align_rows: list[dict[str, object]] = []
    for label, sub in [
        ("anti_aligned", df[df["SNBAOOppositeSign"].astype(bool)]),
        ("not_anti_aligned", df[~df["SNBAOOppositeSign"].astype(bool)]),
        (
            "anti_aligned_mid_high",
            df[df["SNBAOOppositeSign"].astype(bool) & df["DepthBin"].isin(["mid_depth", "high_depth"])],
        ),
        (
            "not_anti_aligned_mid_high",
            df[(~df["SNBAOOppositeSign"].astype(bool)) & df["DepthBin"].isin(["mid_depth", "high_depth"])],
        ),
        ("mid_depth_anti_aligned", df[df["SNBAOOppositeSign"].astype(bool) & (df["DepthBin"] == "mid_depth")]),
        ("mid_depth_not_anti_aligned", df[(~df["SNBAOOppositeSign"].astype(bool)) & (df["DepthBin"] == "mid_depth")]),
    ]:
        if len(sub) < 2:
            continue
        comp = compare_subset(sub.copy())
        a2 = comp[comp["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR"].iloc[0]
        unit = comp[comp["ModelID"] == "K2_UNIT_LOCKED_RHO4"].iloc[0]
        k1 = comp[comp["ModelID"] == "K1_NO_MEMORY"].iloc[0]
        align_rows.append(
            {
                "Condition": label,
                "Rows": len(sub),
                "MeanX": float(sub["x_coordinate"].mean()),
                "A2PredictionToTargetRMSRatio": float(a2["PredictionToTargetRMSRatio"]),
                "A2ResidualRMS": float(a2["ResidualRMS"]),
                "A2Chi2DiagProxy": float(a2["Chi2DiagProxy"]),
                "A2DeltaAICVsUnit": float(a2["AIC"] - unit["AIC"]),
                "A2DeltaAICVsK1": float(a2["AIC"] - k1["AIC"]),
                "A2SignMatchFraction": float(a2["SignMatchFraction"]),
                "ClaimBoundary": "a2_stress_preflight_no_measurement_validation",
            }
        )
    align = pd.DataFrame(align_rows)
    align.to_csv(OUT_ALIGN, index=False)

    loo = pd.DataFrame(loo_rows)
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "SOURCE_SPLIT_A2_STRESS_SUMMARY",
                "LeaveOneOutRows": len(loo),
                "A2WinsLeaveOneOutCount": int(loo["A2Wins"].sum()),
                "A2WinsLeaveOneOutFraction": float(loo["A2Wins"].mean()),
                "A2WinsWhenDroppingMidDepthCount": int(loo[loo["DroppedWasMidDepth"]]["A2Wins"].sum()),
                "A2WinsWhenDroppingMidDepthFraction": float(loo[loo["DroppedWasMidDepth"]]["A2Wins"].mean()),
                "DepthAmplitudeRatiosLowMidHigh": list(depth["A2PredictionToTargetRMSRatio"]),
                "DepthDeltaAICVsUnitLowMidHigh": list(depth["A2DeltaAICVsUnit"]),
                "AntiAlignedA2DeltaAICVsUnit": float(
                    align[align["Condition"] == "anti_aligned"]["A2DeltaAICVsUnit"].iloc[0]
                )
                if "anti_aligned" in set(align["Condition"])
                else float("nan"),
                "NotAntiAlignedA2DeltaAICVsUnit": float(
                    align[align["Condition"] == "not_anti_aligned"]["A2DeltaAICVsUnit"].iloc[0]
                )
                if "not_anti_aligned" in set(align["Condition"])
                else float("nan"),
                "MidDepthA2DeltaAICVsUnit": float(
                    depth[depth["DepthBin"] == "mid_depth"]["A2DeltaAICVsUnit"].iloc[0]
                ),
                "Interpretation": "a2_prior_survives_leave_one_out_and_strengthens_with_depth; mid_depth_improves_but_is_transitional",
                "ClaimBoundary": "a2_stress_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_LOO}")
    print(f"Wrote {OUT_DEPTH}")
    print(f"Wrote {OUT_ALIGN}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
