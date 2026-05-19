#!/usr/bin/env python3
"""Audit whether a mid/high-depth tau projection gain is stable.

This tests the derived idea that the observed source-split amplitude gap may be
an observable projection gain A_tau multiplying the locked K2 backbone in the
memory-active regime. It does not fit K1 or alter W(x).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "tau_gain_stability_audit.csv"
SUMMARY = EVIDENCE / "tau_gain_stability_summary.csv"


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


def gain_from_point(y: float, k2: float) -> float:
    if abs(k2) < 1e-12:
        return float("nan")
    return float(y / k2)


def summarize(df: pd.DataFrame, subset: str) -> dict[str, object]:
    y = df["SourceSplitResponse"].to_numpy(float)
    ya = df["ResidualAfterAlpha"].to_numpy(float)
    k2 = df["K2LockedRho4"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)

    scale = fit_scale(y, k2)
    scale_after = fit_scale(ya, k2)
    pred = scale * k2
    pred_after = scale_after * k2
    point_gains = np.array([gain_from_point(yy, pp) for yy, pp in zip(y, k2, strict=True)], dtype=float)
    usable_gains = point_gains[np.isfinite(point_gains)]

    return {
        "Subset": subset,
        "Rows": len(df),
        "MeanX": float(df["x_coordinate"].mean()),
        "FittedCommonGain": scale,
        "FittedCommonGainAfterAlpha": scale_after,
        "MedianPointGain": float(np.nanmedian(point_gains)),
        "MeanPointGain": float(np.nanmean(point_gains)),
        "PointGainStd": float(np.nanstd(point_gains)),
        "PointGainCoeffVarAbs": float(np.nanstd(usable_gains) / abs(np.nanmean(usable_gains)))
        if len(usable_gains) and abs(np.nanmean(usable_gains)) > 1e-12
        else float("nan"),
        "MinPointGain": float(np.nanmin(point_gains)),
        "MaxPointGain": float(np.nanmax(point_gains)),
        "AllPointGainsPositive": bool(np.all(usable_gains > 0.0)) if len(usable_gains) else False,
        "CommonGainPredictionRMS": rms(pred),
        "TargetRMS": rms(y),
        "CommonGainToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsCommonGainK2": cosine(y, pred),
        "ResidualRMSAfterCommonGain": rms(y - pred),
        "ResidualRMSLockedK2": rms(y - k2),
        "Chi2CommonGain": chi2_diag(y, pred, sigma),
        "Chi2LockedK2": chi2_diag(y, k2, sigma),
        "DeltaChi2CommonGainVsLocked": chi2_diag(y, pred, sigma) - chi2_diag(y, k2, sigma),
        "GainBand": "within_2_to_3"
        if 2.0 <= scale <= 3.0
        else "near_2_to_3"
        if 1.5 <= scale <= 3.5
        else "outside_2_to_3",
        "Interpretation": "stable_memory_active_gain_candidate"
        if subset == "mid_high_depth" and 1.5 <= scale <= 3.5 and np.all(usable_gains > 0.0)
        else "diagnostic_subset",
        "ClaimBoundary": "tau_gain_stability_preflight_no_measurement_validation",
    }


def main() -> None:
    df = pd.read_csv(DECOMP)
    df["PointGainTargetOverK2"] = [
        gain_from_point(y, p) for y, p in zip(df["SourceSplitResponse"], df["K2LockedRho4"], strict=True)
    ]
    df["PointGainAfterAlphaOverK2"] = [
        gain_from_point(y, p) for y, p in zip(df["ResidualAfterAlpha"], df["K2LockedRho4"], strict=True)
    ]
    df["MemoryActive"] = df["DepthBin"].isin(["mid_depth", "high_depth"])
    df["GainWithin2To3"] = df["PointGainTargetOverK2"].between(2.0, 3.0)
    df["GainWithin1p5To3p5"] = df["PointGainTargetOverK2"].between(1.5, 3.5)
    df["ClaimBoundary"] = "tau_gain_stability_preflight_no_measurement_validation"
    df.to_csv(OUT, index=False)

    stable = df["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    subsets = [
        ("all_points", df),
        ("sign_stable_only", df[stable]),
        ("mid_high_depth", df[df["MemoryActive"]]),
        ("mid_high_sign_stable", df[df["MemoryActive"] & stable]),
        ("high_depth", df[df["DepthBin"] == "high_depth"]),
        ("low_depth", df[df["DepthBin"] == "low_depth"]),
    ]
    summary = pd.DataFrame([summarize(sub.copy(), name) for name, sub in subsets if len(sub) >= 2])
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
