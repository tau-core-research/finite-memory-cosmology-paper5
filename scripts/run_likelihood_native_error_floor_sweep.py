#!/usr/bin/env python3
"""Sweep target-fraction error floors for likelihood-native source-split scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
OUT = ROOT / "evidence" / "source_split_likelihood_native_error_floor_sweep.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_error_floor_sweep_summary.csv"


def model_predictions(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> list[tuple[str, np.ndarray, int]]:
    rows: list[tuple[str, np.ndarray, int]] = [
        ("K1_NO_MEMORY", k1, 0),
        ("K2_LOCKED_RHO4", w_k2_locked(x, rho=4.0) * k1, 0),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1))
    return rows


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    native_sigma = data["K1Sigma"].to_numpy(float)
    abs_y = np.abs(y)

    rows = []
    fractions = np.round(np.linspace(0.0, 0.5, 51), 4)
    for fraction in fractions:
        sigma = np.maximum(native_sigma, fraction * abs_y)
        cov = np.diag(sigma * sigma)
        for model_id, pred, k in model_predictions(x, y, k1):
            c2 = chi2(y, pred, cov)
            rows.append(
                {
                    "TargetFractionFloor": float(fraction),
                    "ModelID": model_id,
                    "ParameterCount": k,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "MeanSigmaEffective": float(np.mean(sigma)),
                    "MinSigmaEffective": float(np.min(sigma)),
                    "MaxSigmaEffective": float(np.max(sigma)),
                    "ClaimBoundary": "error_floor_sweep_only_no_measurement_validation",
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary_rows = []
    first_k2_best = None
    first_k2_beats_poly = None
    for fraction, group in output.groupby("TargetFractionFloor", sort=True):
        best = group.loc[group["AIC"].idxmin()]
        k2_aic = float(group.loc[group["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
        k1_aic = float(group.loc[group["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
        best_poly_aic = float(group[group["ModelID"].str.startswith("POLY")]["AIC"].min())
        k2_best = str(best["ModelID"]) == "K2_LOCKED_RHO4"
        k2_beats_poly = k2_aic < best_poly_aic
        if first_k2_best is None and k2_best:
            first_k2_best = float(fraction)
        if first_k2_beats_poly is None and k2_beats_poly:
            first_k2_beats_poly = float(fraction)
        summary_rows.append(
            {
                "TargetFractionFloor": float(fraction),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2BestModel": k2_best,
                "K2BeatsBestPoly": k2_beats_poly,
                "ClaimBoundary": "error_floor_sweep_only_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary["FirstFloorWhereK2Best"] = first_k2_best if first_k2_best is not None else np.nan
    summary["FirstFloorWhereK2BeatsBestPoly"] = (
        first_k2_beats_poly if first_k2_beats_poly is not None else np.nan
    )
    summary["Interpretation"] = np.where(
        summary["K2BestModel"],
        "k2_best_under_this_floor",
        np.where(summary["K2BeatsBestPoly"], "k2_beats_poly_but_not_all_controls", "poly_or_control_dominates"),
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
