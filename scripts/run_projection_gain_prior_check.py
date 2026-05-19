#!/usr/bin/env python3
"""Check predeclared tau projection gain priors against source-split data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "projection_gain_prior_check.csv"
SUMMARY = EVIDENCE / "projection_gain_prior_summary.csv"


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


def fit_scale(y: np.ndarray, k2: np.ndarray) -> float:
    denom = float(np.dot(k2, k2))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(k2, y) / denom)


def summarize(df: pd.DataFrame, subset: str, gain_id: str, gain: float) -> dict[str, object]:
    y = df["SourceSplitResponse"].to_numpy(float)
    k2 = df["K2LockedRho4"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)
    pred = gain * k2
    c2 = chi2_diag(y, pred, sigma)
    return {
        "Subset": subset,
        "GainID": gain_id,
        "GainValue": gain,
        "Rows": len(df),
        "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsPrediction": cosine(y, pred),
        "ResidualRMS": rms(y - pred),
        "Chi2DiagProxy": c2,
        "AICFixedGain": c2,
        "ClaimBoundary": "projection_gain_prior_preflight_no_measurement_validation",
    }


def main() -> None:
    df = pd.read_csv(DECOMP)
    high = df[df["DepthBin"] == "high_depth"]
    diagnostic_high_gain = fit_scale(high["SourceSplitResponse"].to_numpy(float), high["K2LockedRho4"].to_numpy(float))

    gains = [
        ("A_TAU_UNIT_GAIN_1", 1.0),
        ("A_TAU_SYMMETRIC_PRIOR_2", 2.0),
        ("A_TAU_HIGH_DEPTH_DIAGNOSTIC", diagnostic_high_gain),
    ]

    point_rows: list[dict[str, object]] = []
    for gain_id, gain in gains:
        for _, row in df.iterrows():
            pred = gain * float(row["K2LockedRho4"])
            point_rows.append(
                {
                    "GainID": gain_id,
                    "GainValue": gain,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "DepthBin": row["DepthBin"],
                    "SourceSplitResponse": float(row["SourceSplitResponse"]),
                    "K2LockedRho4": float(row["K2LockedRho4"]),
                    "GainPrediction": pred,
                    "GainResidual": float(row["SourceSplitResponse"] - pred),
                    "ExplainedFractionProxy": 1.0 - abs(float(row["SourceSplitResponse"] - pred))
                    / abs(float(row["SourceSplitResponse"])),
                    "SignStableTemplate": bool(row["SignStableTemplate"]),
                    "ClaimBoundary": "projection_gain_prior_preflight_no_measurement_validation",
                }
            )
    pd.DataFrame(point_rows).to_csv(OUT, index=False)

    subsets = [
        ("all_points", df),
        ("low_depth", df[df["DepthBin"] == "low_depth"]),
        ("mid_depth", df[df["DepthBin"] == "mid_depth"]),
        ("high_depth", df[df["DepthBin"] == "high_depth"]),
        ("mid_high_depth", df[df["DepthBin"].isin(["mid_depth", "high_depth"])]),
    ]
    summary_rows: list[dict[str, object]] = []
    for subset, sub in subsets:
        for gain_id, gain in gains:
            summary_rows.append(summarize(sub, subset, gain_id, gain))
    summary = pd.DataFrame(summary_rows)
    locked = summary[summary["GainID"] == "A_TAU_UNIT_GAIN_1"][["Subset", "Chi2DiagProxy", "ResidualRMS"]].rename(
        columns={"Chi2DiagProxy": "UnitGainChi2", "ResidualRMS": "UnitGainResidualRMS"}
    )
    summary = summary.merge(locked, on="Subset", how="left")
    summary["DeltaChi2VsUnitGain"] = summary["Chi2DiagProxy"] - summary["UnitGainChi2"]
    summary["DeltaResidualRMSVsUnitGain"] = summary["ResidualRMS"] - summary["UnitGainResidualRMS"]
    summary["Interpretation"] = np.where(
        (summary["GainID"] == "A_TAU_SYMMETRIC_PRIOR_2")
        & (summary["Subset"].isin(["high_depth", "mid_high_depth"]))
        & (summary["PredictionToTargetRMSRatio"] > 0.8),
        "symmetric_gain_prior_recovers_memory_active_amplitude",
        "diagnostic_gain_contrast",
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
