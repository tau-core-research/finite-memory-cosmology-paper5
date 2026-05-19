#!/usr/bin/env python3
"""Stress locked A2 under simple SN/BAO transform variants.

This is a transform-robustness preflight only. It recomputes source-split
targets from already exported public residual preflight tables, keeps K1/K2/A2
fixed, and reports whether the memory-active support survives simple declared
transform variants. It is not a likelihood-native measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

SN_ROWS = EVIDENCE / "sn_residual_preflight.csv"
BAO_ROWS = EVIDENCE / "bao_residual_transform_preflight.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_transform_variant_robustness.csv"
SUMMARY = EVIDENCE / "k2_a2_transform_variant_robustness_summary.csv"


def grid_edges(grid: np.ndarray) -> np.ndarray:
    mids = (grid[:-1] + grid[1:]) / 2.0
    return np.concatenate([[max(0.0, grid[0] - (mids[0] - grid[0]))], mids, [grid[-1] + (grid[-1] - mids[-1])]])


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def weighted_mean_and_sigma(values: np.ndarray, sigma: np.ndarray, weighted: bool) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    if weighted:
        weights = np.where(sigma > 0.0, 1.0 / (sigma * sigma), 0.0)
        denom = float(np.sum(weights))
        if denom <= 0.0:
            return float("nan"), float("nan")
        mean = float(np.sum(weights * values) / denom)
        sigma_mean = float(np.sqrt(1.0 / denom))
        return mean, sigma_mean
    mean = float(np.mean(values))
    sigma_mean = float(np.sqrt(np.sum(sigma * sigma)) / len(values))
    return mean, sigma_mean


def sn_vector(grid: np.ndarray, mode: str) -> np.ndarray:
    sn = pd.read_csv(SN_ROWS)
    z = sn["z"].to_numpy(float)
    raw = sn["RawResidualMu"].to_numpy(float)
    centered = sn["CenteredResidualMu"].to_numpy(float)
    sigma = sn["SigmaDiag"].to_numpy(float)
    values = raw if "raw" in mode else centered
    weighted = "weighted" in mode

    edges = grid_edges(grid)
    bin_index = np.digitize(z, edges) - 1
    out = []
    for idx in range(len(grid)):
        members = bin_index == idx
        mean, sigma_mean = weighted_mean_and_sigma(values[members], sigma[members], weighted)
        out.append(mean / sigma_mean if sigma_mean > 0.0 else float("nan"))
    return np.asarray(out, dtype=float)


def bao_vector(grid: np.ndarray, mode: str) -> np.ndarray:
    bao = pd.read_csv(BAO_ROWS)
    z = bao["z"].to_numpy(float)
    values = bao["LogResidual"].to_numpy(float)
    sigma = bao["SigmaDiag"].to_numpy(float)
    weighted = "invvar" in mode

    out = []
    for target_z in grid:
        distances = np.abs(z - float(target_z))
        nearest = float(np.min(distances))
        members = distances == nearest
        mean, sigma_mean = weighted_mean_and_sigma(values[members], sigma[members], weighted)
        out.append(mean / sigma_mean if sigma_mean > 0.0 else float("nan"))
    return np.asarray(out, dtype=float)


def chi2_unit(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(np.sum(residual * residual))


def aic(chi2_value: float, k: int) -> float:
    return float(chi2_value + 2 * k)


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray, unit: np.ndarray, a2_pred: np.ndarray):
    rows: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_UNIT_LOCKED_RHO4", unit, 0, "locked_memory_backbone"),
        ("K2_SOURCE_SPLIT_A2_PRIOR_V1", a2_pred, 0, "locked_projection_prior"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    if len(y) >= 4:
        coeff = np.polyfit(x, y, 2)
        rows.append(("POLY_DEG2", np.polyval(coeff, x), 3, "overfit_risk_control"))
    return rows


def main() -> None:
    pred = pd.read_csv(PRED).sort_values("GridIndex").reset_index(drop=True)
    grid = pred["z_grid"].to_numpy(float)
    x = pred["x_coordinate"].to_numpy(float)
    zones = np.array([depth_zone(v) for v in x])

    sn_modes = [
        "weighted_centered_sn",
        "weighted_raw_sn",
        "unweighted_centered_sn",
    ]
    bao_modes = [
        "nearest_invvar_bao",
        "nearest_equal_bao",
    ]
    subsets = {
        "all_depth": np.ones(len(pred), dtype=bool),
        "mid_high_memory_active": zones != "low_depth",
        "high_depth": zones == "high_depth",
    }

    rows = []
    for sn_mode in sn_modes:
        sn = sn_vector(grid, sn_mode)
        for bao_mode in bao_modes:
            bao = bao_vector(grid, bao_mode)
            y_full = sn - bao
            finite = np.isfinite(y_full)
            for subset_id, subset_mask in subsets.items():
                mask = subset_mask & finite
                if int(mask.sum()) < 3:
                    continue
                y = y_full[mask]
                xx = x[mask]
                k1 = pred.loc[mask, "K1Response"].to_numpy(float)
                unit = pred.loc[mask, "K2UnitLockedRho4"].to_numpy(float)
                a2_pred = pred.loc[mask, "K2SourceSplitA2Prediction"].to_numpy(float)
                for model_id, values, k, model_class in model_rows(xx, y, k1, unit, a2_pred):
                    c2 = chi2_unit(y, values)
                    rows.append(
                        {
                            "TransformVariantID": f"{sn_mode}__{bao_mode}",
                            "SNMode": sn_mode,
                            "BAOMode": bao_mode,
                            "SubsetID": subset_id,
                            "Rows": int(mask.sum()),
                            "ModelID": model_id,
                            "ModelClass": model_class,
                            "ParameterCount": k,
                            "Chi2UnitProxy": c2,
                            "AIC": aic(c2, k),
                            "MeanAbsResidual": float(np.mean(np.abs(y - values))),
                            "TargetRMS": float(np.sqrt(np.mean(y * y))),
                            "PredictionRMS": float(np.sqrt(np.mean(values * values))),
                            "SignMatchFraction": float(np.mean(np.sign(values) == np.sign(y))),
                            "ClaimBoundary": "transform_variant_robustness_no_measurement_validation",
                        }
                    )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (variant, subset), group in detail.groupby(["TransformVariantID", "SubsetID"], sort=False):
        a2_row = group[group["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")].iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        unit_row = group[group["ModelID"].eq("K2_UNIT_LOCKED_RHO4")].iloc[0]
        poly = group[group["ModelID"].str.startswith("POLY")]
        best_poly_aic = float(poly["AIC"].min()) if not poly.empty else float("nan")
        best_model = group.sort_values("AIC").iloc[0]
        summary_rows.append(
            {
                "TransformVariantID": variant,
                "SubsetID": subset,
                "Rows": int(a2_row["Rows"]),
                "BestModel": best_model["ModelID"],
                "A2AIC": float(a2_row["AIC"]),
                "K1AIC": float(k1_row["AIC"]),
                "UnitK2AIC": float(unit_row["AIC"]),
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_A2_minus_K1": float(a2_row["AIC"] - k1_row["AIC"]),
                "DeltaAIC_A2_minus_UnitK2": float(a2_row["AIC"] - unit_row["AIC"]),
                "DeltaAIC_A2_minus_BestPoly": float(a2_row["AIC"] - best_poly_aic)
                if not np.isnan(best_poly_aic)
                else "",
                "A2ImprovesOverK1": bool(a2_row["AIC"] < k1_row["AIC"]),
                "A2ImprovesOverUnitK2": bool(a2_row["AIC"] < unit_row["AIC"]),
                "A2BeatsBestPoly": bool(a2_row["AIC"] < best_poly_aic) if not np.isnan(best_poly_aic) else "",
                "ClaimBoundary": "transform_variant_robustness_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
