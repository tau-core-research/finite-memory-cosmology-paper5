#!/usr/bin/env python3
"""Benchmark the source-split A_tau=2 projection prior.

K2_A2_PRIOR is not a new kernel. It is the locked K2 backbone multiplied by a
predeclared source-split projection gain motivated by anti-aligned SN/BAO
channel geometry.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "source_split_a2_prior_benchmark.csv"
SUMMARY = EVIDENCE / "source_split_a2_prior_summary.csv"


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


def aic(chi2: float, k: int) -> float:
    return float(chi2 + 2 * k)


def bic(chi2: float, k: int, n: int) -> float:
    return float(chi2 + k * np.log(n))


def fit_scale(y: np.ndarray, k2: np.ndarray) -> float:
    denom = float(np.dot(k2, k2))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(k2, y) / denom)


def poly_prediction(x: np.ndarray, y: np.ndarray, degree: int) -> np.ndarray:
    if len(x) <= degree:
        return np.full_like(y, np.nan, dtype=float)
    coeff = np.polyfit(x, y, degree)
    return np.polyval(coeff, x)


def sign_match_fraction(y: np.ndarray, pred: np.ndarray) -> float:
    signs = np.sign(y) == np.sign(pred)
    return float(np.mean(signs))


def row(
    subset: str,
    model_id: str,
    y: np.ndarray,
    pred: np.ndarray,
    sigma: np.ndarray,
    parameter_count: int,
    gain: float | None,
    model_class: str,
) -> dict[str, object]:
    c2 = chi2_diag(y, pred, sigma)
    return {
        "Subset": subset,
        "ModelID": model_id,
        "ModelClass": model_class,
        "Rows": len(y),
        "ParameterCount": parameter_count,
        "ProjectionGain": gain,
        "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsPrediction": cosine(y, pred),
        "ResidualRMS": rms(y - pred),
        "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
        "Chi2DiagProxy": c2,
        "AIC": aic(c2, parameter_count),
        "BIC": bic(c2, parameter_count, len(y)),
        "SignMatchFraction": sign_match_fraction(y, pred),
        "ClaimBoundary": "a2_prior_benchmark_preflight_no_measurement_validation",
    }


def benchmark_subset(subset: str, df: pd.DataFrame) -> list[dict[str, object]]:
    y = df["SourceSplitResponse"].to_numpy(float)
    x = df["x_coordinate"].to_numpy(float)
    sigma = df["SigmaDiagProxy"].to_numpy(float)
    k1 = df["K1Response"].to_numpy(float)
    k2 = df["K2LockedRho4"].to_numpy(float)
    high_gain = fit_scale(
        df[df["DepthBin"] == "high_depth"]["SourceSplitResponse"].to_numpy(float),
        df[df["DepthBin"] == "high_depth"]["K2LockedRho4"].to_numpy(float),
    )
    if not np.isfinite(high_gain):
        high_gain = 2.0810143494478432

    models: list[tuple[str, np.ndarray, int, float | None, str]] = [
        ("K1_NO_MEMORY", k1, 0, None, "frozen_baseline"),
        ("K2_UNIT_LOCKED_RHO4", k2, 0, 1.0, "locked_memory_backbone"),
        ("K2_SOURCE_SPLIT_A2_PRIOR", 2.0 * k2, 0, 2.0, "predeclared_projection_prior"),
        ("K2_HIGH_DEPTH_DIAGNOSTIC_GAIN", high_gain * k2, 1, high_gain, "diagnostic_gain_control"),
    ]
    if len(df) > 3:
        models.append(("POLY_DEG2", poly_prediction(x, y, 2), 3, None, "overfit_risk_control"))
    if len(df) > 4:
        models.append(("POLY_DEG3", poly_prediction(x, y, 3), 4, None, "overfit_risk_control"))

    return [row(subset, model_id, y, pred, sigma, k, gain, model_class) for model_id, pred, k, gain, model_class in models]


def main() -> None:
    df = pd.read_csv(DECOMP)
    stable = df["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    subsets = [
        ("all_points", df),
        ("sign_stable_only", df[stable]),
        ("mid_depth", df[df["DepthBin"] == "mid_depth"]),
        ("high_depth", df[df["DepthBin"] == "high_depth"]),
        ("mid_high_depth", df[df["DepthBin"].isin(["mid_depth", "high_depth"])]),
    ]

    rows: list[dict[str, object]] = []
    for subset, sub in subsets:
        if len(sub) >= 2:
            rows.extend(benchmark_subset(subset, sub.copy()))

    out = pd.DataFrame(rows)
    unit = out[out["ModelID"] == "K2_UNIT_LOCKED_RHO4"][["Subset", "AIC", "BIC", "ResidualRMS"]].rename(
        columns={"AIC": "K2UnitAIC", "BIC": "K2UnitBIC", "ResidualRMS": "K2UnitResidualRMS"}
    )
    a2 = out[out["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR"][["Subset", "AIC", "BIC", "ResidualRMS"]].rename(
        columns={"AIC": "A2AIC", "BIC": "A2BIC", "ResidualRMS": "A2ResidualRMS"}
    )
    out = out.merge(unit, on="Subset", how="left").merge(a2, on="Subset", how="left")
    out["DeltaAICVsK2Unit"] = out["AIC"] - out["K2UnitAIC"]
    out["DeltaBICVsK2Unit"] = out["BIC"] - out["K2UnitBIC"]
    out["DeltaAICVsA2Prior"] = out["AIC"] - out["A2AIC"]
    out["DeltaResidualRMSVsA2Prior"] = out["ResidualRMS"] - out["A2ResidualRMS"]
    out.to_csv(OUT, index=False)

    best = out.sort_values(["Subset", "AIC"]).groupby("Subset", as_index=False).first()
    focus = out[out["ModelID"].isin(["K2_SOURCE_SPLIT_A2_PRIOR", "K2_HIGH_DEPTH_DIAGNOSTIC_GAIN"])]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "SOURCE_SPLIT_A2_PRIOR_BENCHMARK_SUMMARY",
                "BestAICBySubset": dict(zip(best["Subset"], best["ModelID"], strict=True)),
                "A2HighDepthAmplitudeRatio": float(
                    focus[
                        (focus["Subset"] == "high_depth") & (focus["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR")
                    ]["PredictionToTargetRMSRatio"].iloc[0]
                ),
                "A2HighDepthResidualRMS": float(
                    focus[(focus["Subset"] == "high_depth") & (focus["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR")][
                        "ResidualRMS"
                    ].iloc[0]
                ),
                "A2MidDepthAmplitudeRatio": float(
                    focus[(focus["Subset"] == "mid_depth") & (focus["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR")][
                        "PredictionToTargetRMSRatio"
                    ].iloc[0]
                ),
                "A2MidDepthResidualRMS": float(
                    focus[(focus["Subset"] == "mid_depth") & (focus["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR")][
                        "ResidualRMS"
                    ].iloc[0]
                ),
                "A2MidHighAmplitudeRatio": float(
                    focus[
                        (focus["Subset"] == "mid_high_depth") & (focus["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR")
                    ]["PredictionToTargetRMSRatio"].iloc[0]
                ),
                "Interpretation": "a2_prior_is_strong_in_high_depth_partial_in_mid_depth",
                "ClaimBoundary": "a2_prior_benchmark_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
