#!/usr/bin/env python3
"""Decompose the current source-split target around locked K2.

This diagnostic asks whether the locked K2 response captures the backbone of the
source-split residual before and after the AS_DECLARED alpha optical control.
It does not refit K1, does not change rho, and does not authorize a measurement
claim.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
ALPHA = EVIDENCE / "alpha_as_declared_preflight.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
SIGMA = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"

OUT = EVIDENCE / "k2_residual_decomposition.csv"
SUMMARY = EVIDENCE / "k2_residual_decomposition_summary.csv"


def sign(value: float) -> int:
    if not math.isfinite(value) or abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def mean_abs(v: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(v, dtype=float))))


def chi2_diag(y: np.ndarray, m: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(m) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - m[usable]) / sigma[usable]
    return float(np.dot(r, r))


def k2_locked(x: np.ndarray, k1: np.ndarray) -> np.ndarray:
    return np.asarray(k1, dtype=float) * (1.0 + 4.0 * np.asarray(x, dtype=float) ** 3)


def depth_bin(x: float) -> str:
    if x < 0.5:
        return "low_depth"
    if x < 0.8:
        return "mid_depth"
    return "high_depth"


def explained_fraction_proxy(y: float, pred: float) -> float:
    if abs(y) < 1e-12:
        return float("nan")
    return float(1.0 - abs(y - pred) / abs(y))


def vector_summary(frame: pd.DataFrame, label: str, mask: np.ndarray) -> dict[str, object]:
    sub = frame.loc[mask].copy()
    if sub.empty:
        return {
            "Subset": label,
            "Rows": 0,
            "CosineTargetVsK2": float("nan"),
            "CosineAfterAlphaVsK2": float("nan"),
            "TargetRMS": float("nan"),
            "K2RMS": float("nan"),
            "ResidualMinusK2RMS": float("nan"),
            "ResidualAfterAlphaMinusK2RMS": float("nan"),
            "MeanAbsTargetMinusK2": float("nan"),
            "MeanAbsAfterAlphaMinusK2": float("nan"),
            "Chi2TargetVsK2": float("nan"),
            "Chi2AfterAlphaVsK2": float("nan"),
            "K2SignMatchFraction": float("nan"),
            "AfterAlphaK2SignMatchFraction": float("nan"),
            "MeanExplainedFractionProxy": float("nan"),
            "MeanAfterAlphaExplainedFractionProxy": float("nan"),
        }

    y = sub["SourceSplitResponse"].to_numpy(float)
    ya = sub["ResidualAfterAlpha"].to_numpy(float)
    k2 = sub["K2LockedRho4"].to_numpy(float)
    sigma = sub["SigmaDiagProxy"].to_numpy(float)
    sign_match = [sign(yy) == sign(pp) for yy, pp in zip(y, k2, strict=True)]
    sign_match_after = [sign(yy) == sign(pp) for yy, pp in zip(ya, k2, strict=True)]
    return {
        "Subset": label,
        "Rows": len(sub),
        "CosineTargetVsK2": cosine(y, k2),
        "CosineAfterAlphaVsK2": cosine(ya, k2),
        "DeltaCosineAfterAlpha": cosine(ya, k2) - cosine(y, k2),
        "TargetRMS": rms(y),
        "ResidualAfterAlphaRMS": rms(ya),
        "K2RMS": rms(k2),
        "K2ToTargetRMSRatio": rms(k2) / rms(y) if rms(y) > 0.0 else float("nan"),
        "K2ToAfterAlphaRMSRatio": rms(k2) / rms(ya) if rms(ya) > 0.0 else float("nan"),
        "ResidualMinusK2RMS": rms(y - k2),
        "ResidualAfterAlphaMinusK2RMS": rms(ya - k2),
        "MeanAbsTargetMinusK2": mean_abs(y - k2),
        "MeanAbsAfterAlphaMinusK2": mean_abs(ya - k2),
        "Chi2TargetVsK2": chi2_diag(y, k2, sigma),
        "Chi2AfterAlphaVsK2": chi2_diag(ya, k2, sigma),
        "K2SignMatchFraction": float(np.mean(sign_match)),
        "AfterAlphaK2SignMatchFraction": float(np.mean(sign_match_after)),
        "MeanExplainedFractionProxy": float(np.nanmean(sub["K2ExplainedFractionProxy"])),
        "MeanAfterAlphaExplainedFractionProxy": float(np.nanmean(sub["K2AfterAlphaExplainedFractionProxy"])),
    }


def main() -> None:
    target = pd.read_csv(TARGET)
    alpha = pd.read_csv(ALPHA)
    k1 = pd.read_csv(K1)
    sigma = pd.read_csv(SIGMA)[["GridIndex", "SigmaMaxNativeScatter"]]

    usable = target[
        target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
        & target["SourceSplitResponse"].notna()
    ][
        [
            "GridIndex",
            "z_grid",
            "SourceSplitResponse",
            "SNStandardizedResidual",
            "BAOStandardizedResidual",
            "SignStableTemplate",
        ]
    ]

    alpha_choice = (
        alpha[alpha["ExtractionID"] == "PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR"]
        [["GridIndex", "ExtractionID", "Alpha", "AlphaASDeclaredPreview"]]
        .copy()
    )
    merged = (
        usable.merge(
            k1[["GridIndex", "x_coordinate", "K1Response"]],
            on="GridIndex",
            how="inner",
        )
        .merge(sigma, on="GridIndex", how="left")
        .merge(alpha_choice, on="GridIndex", how="left")
        .sort_values("GridIndex")
    )

    merged["K2LockedRho4"] = k2_locked(merged["x_coordinate"], merged["K1Response"])
    merged["ResidualAfterAlpha"] = merged["SourceSplitResponse"] - merged["AlphaASDeclaredPreview"]
    merged["TargetMinusK2"] = merged["SourceSplitResponse"] - merged["K2LockedRho4"]
    merged["ResidualAfterAlphaMinusK2"] = merged["ResidualAfterAlpha"] - merged["K2LockedRho4"]
    merged["K2ExplainedFractionProxy"] = [
        explained_fraction_proxy(y, p)
        for y, p in zip(merged["SourceSplitResponse"], merged["K2LockedRho4"], strict=True)
    ]
    merged["K2AfterAlphaExplainedFractionProxy"] = [
        explained_fraction_proxy(y, p)
        for y, p in zip(merged["ResidualAfterAlpha"], merged["K2LockedRho4"], strict=True)
    ]
    merged["K2SignMatchesTarget"] = [
        sign(y) == sign(p) for y, p in zip(merged["SourceSplitResponse"], merged["K2LockedRho4"], strict=True)
    ]
    merged["K2SignMatchesAfterAlpha"] = [
        sign(y) == sign(p) for y, p in zip(merged["ResidualAfterAlpha"], merged["K2LockedRho4"], strict=True)
    ]
    merged["DepthBin"] = [depth_bin(float(x)) for x in merged["x_coordinate"]]
    merged["ClaimBoundary"] = "k2_residual_decomposition_preflight_no_measurement_validation"

    out_cols = [
        "GridIndex",
        "z_grid",
        "x_coordinate",
        "DepthBin",
        "SignStableTemplate",
        "SourceSplitResponse",
        "SNStandardizedResidual",
        "BAOStandardizedResidual",
        "AlphaASDeclaredPreview",
        "ResidualAfterAlpha",
        "K1Response",
        "K2LockedRho4",
        "SigmaDiagProxy",
        "TargetMinusK2",
        "ResidualAfterAlphaMinusK2",
        "K2ExplainedFractionProxy",
        "K2AfterAlphaExplainedFractionProxy",
        "K2SignMatchesTarget",
        "K2SignMatchesAfterAlpha",
        "ClaimBoundary",
    ]
    merged = merged.rename(columns={"SigmaMaxNativeScatter": "SigmaDiagProxy"})
    merged[out_cols].to_csv(OUT, index=False)

    stable = merged["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy()
    summaries: list[dict[str, object]] = []
    summaries.append(vector_summary(merged, "all_points", np.ones(len(merged), dtype=bool)))
    summaries.append(vector_summary(merged, "sign_stable_only", stable))
    summaries.append(vector_summary(merged, "sign_unstable_only", ~stable))
    for bin_name in ["low_depth", "mid_depth", "high_depth"]:
        summaries.append(vector_summary(merged, bin_name, (merged["DepthBin"] == bin_name).to_numpy()))

    summary = pd.DataFrame(summaries)
    summary["AlphaExtractionID"] = "PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR"
    summary["K2Kernel"] = "W(x)=1+4*x^3"
    summary["Interpretation"] = np.where(
        (summary["K2ToTargetRMSRatio"] < 0.25) & (summary["CosineTargetVsK2"] > 0.5),
        "k2_captures_direction_more_than_amplitude",
        "k2_direction_or_amplitude_needs_careful_reading",
    )
    summary["ClaimBoundary"] = "k2_residual_decomposition_preflight_no_measurement_validation"
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
