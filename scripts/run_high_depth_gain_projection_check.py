#!/usr/bin/env python3
"""Apply high-depth A_tau to all zones as a projection-gain check."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "high_depth_gain_projection_check.csv"
SUMMARY = EVIDENCE / "high_depth_gain_projection_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def fit_scale(y: np.ndarray, k2: np.ndarray) -> float:
    denom = float(np.dot(k2, k2))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(k2, y) / denom)


def chi2_diag(y: np.ndarray, pred: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(pred) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - pred[usable]) / sigma[usable]
    return float(np.dot(r, r))


def summarize(df: pd.DataFrame, subset: str, gain: float) -> dict[str, object]:
    y = df["SourceSplitResponse"].to_numpy(float)
    pred = df["HighDepthGainPrediction"].to_numpy(float)
    locked = df["K2LockedRho4"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)
    return {
        "Subset": subset,
        "Rows": len(df),
        "AppliedHighDepthGain": gain,
        "TargetRMS": rms(y),
        "LockedK2RMS": rms(locked),
        "HighDepthGainPredictionRMS": rms(pred),
        "LockedK2ToTargetRMSRatio": rms(locked) / rms(y) if rms(y) > 0.0 else float("nan"),
        "HighDepthGainToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsLockedK2": cosine(y, locked),
        "CosineTargetVsHighDepthGainPrediction": cosine(y, pred),
        "ResidualRMSLockedK2": rms(y - locked),
        "ResidualRMSHighDepthGainPrediction": rms(y - pred),
        "Chi2LockedK2": chi2_diag(y, locked, sigma),
        "Chi2HighDepthGainPrediction": chi2_diag(y, pred, sigma),
        "DeltaChi2HighDepthGainVsLocked": chi2_diag(y, pred, sigma) - chi2_diag(y, locked, sigma),
        "Interpretation": "coherent_under_high_depth_gain"
        if subset == "high_depth" and rms(y - pred) < rms(y - locked)
        else "transitional_or_baseline_dominated",
        "ClaimBoundary": "high_depth_gain_projection_preflight_no_measurement_validation",
    }


def main() -> None:
    df = pd.read_csv(DECOMP)
    high = df[df["DepthBin"] == "high_depth"]
    gain = fit_scale(high["SourceSplitResponse"].to_numpy(float), high["K2LockedRho4"].to_numpy(float))

    df["AppliedHighDepthGain"] = gain
    df["HighDepthGainPrediction"] = gain * df["K2LockedRho4"]
    df["HighDepthGainResidual"] = df["SourceSplitResponse"] - df["HighDepthGainPrediction"]
    df["HighDepthGainExplainedFractionProxy"] = 1.0 - (
        np.abs(df["HighDepthGainResidual"]) / np.abs(df["SourceSplitResponse"])
    )
    df["ClaimBoundary"] = "high_depth_gain_projection_preflight_no_measurement_validation"
    df.to_csv(OUT, index=False)

    rows = [summarize(df, "all_points", gain)]
    for subset in ["low_depth", "mid_depth", "high_depth"]:
        rows.append(summarize(df[df["DepthBin"] == subset], subset, gain))
    stable = df["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    rows.append(summarize(df[stable], "sign_stable_only", gain))
    rows.append(summarize(df[df["DepthBin"].isin(["mid_depth", "high_depth"])], "mid_high_depth", gain))
    pd.DataFrame(rows).to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
