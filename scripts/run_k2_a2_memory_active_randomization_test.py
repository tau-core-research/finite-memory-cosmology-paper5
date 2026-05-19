#!/usr/bin/env python3
"""Randomization controls for the locked A2 memory-active preflight signal.

The locked A2 prediction is not refit. For each simple transform variant, this
script compares the observed A2 residual score with two exact/randomization
controls:

- sign-flip control: preserves target magnitudes but flips signs;
- permutation control: preserves target values but breaks depth ordering.

This is a preflight robustness test only, not a measurement validation.
"""

from __future__ import annotations

from itertools import permutations, product
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

SN_ROWS = EVIDENCE / "sn_residual_preflight.csv"
BAO_ROWS = EVIDENCE / "bao_residual_transform_preflight.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_memory_active_randomization_test.csv"
SUMMARY = EVIDENCE / "k2_a2_memory_active_randomization_summary.csv"


def grid_edges(grid: np.ndarray) -> np.ndarray:
    mids = (grid[:-1] + grid[1:]) / 2.0
    return np.concatenate([[max(0.0, grid[0] - (mids[0] - grid[0]))], mids, [grid[-1] + (grid[-1] - mids[-1])]])


def weighted_mean_and_sigma(values: np.ndarray, sigma: np.ndarray, weighted: bool) -> tuple[float, float]:
    if len(values) == 0:
        return float("nan"), float("nan")
    if weighted:
        weights = np.where(sigma > 0.0, 1.0 / (sigma * sigma), 0.0)
        denom = float(np.sum(weights))
        if denom <= 0.0:
            return float("nan"), float("nan")
        return float(np.sum(weights * values) / denom), float(np.sqrt(1.0 / denom))
    return float(np.mean(values)), float(np.sqrt(np.sum(sigma * sigma)) / len(values))


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


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def chi2_unit(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(np.sum(residual * residual))


def exact_sign_flip_scores(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    mags = np.abs(y)
    scores = []
    for signs in product([-1.0, 1.0], repeat=len(y)):
        scores.append(chi2_unit(mags * np.asarray(signs), pred))
    return np.asarray(scores, dtype=float)


def exact_permutation_scores(y: np.ndarray, pred: np.ndarray) -> np.ndarray:
    scores = []
    for order in permutations(range(len(y))):
        scores.append(chi2_unit(y[list(order)], pred))
    return np.asarray(scores, dtype=float)


def empirical_p_less_equal(scores: np.ndarray, observed: float) -> float:
    return float(np.mean(scores <= observed))


def main() -> None:
    pred = pd.read_csv(PRED).sort_values("GridIndex").reset_index(drop=True)
    grid = pred["z_grid"].to_numpy(float)
    x = pred["x_coordinate"].to_numpy(float)
    zones = np.array([depth_zone(v) for v in x])
    a2_full = pred["K2SourceSplitA2Prediction"].to_numpy(float)

    sn_modes = ["weighted_centered_sn", "weighted_raw_sn", "unweighted_centered_sn"]
    bao_modes = ["nearest_invvar_bao", "nearest_equal_bao"]
    subsets = {
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
                a2 = a2_full[mask]
                observed = chi2_unit(y, a2)
                sign_scores = exact_sign_flip_scores(y, a2)
                perm_scores = exact_permutation_scores(y, a2)
                rows.extend(
                    [
                        {
                            "TransformVariantID": f"{sn_mode}__{bao_mode}",
                            "SubsetID": subset_id,
                            "ControlID": "EXACT_SIGN_FLIP_MAGNITUDE_CONTROL",
                            "Rows": len(y),
                            "ObservedA2Chi2": observed,
                            "ControlCount": len(sign_scores),
                            "ControlMeanChi2": float(np.mean(sign_scores)),
                            "ControlMedianChi2": float(np.median(sign_scores)),
                            "ControlMinChi2": float(np.min(sign_scores)),
                            "EmpiricalP_ControlLEObserved": empirical_p_less_equal(sign_scores, observed),
                            "ObservedBeatsControlMedian": bool(observed < np.median(sign_scores)),
                            "ClaimBoundary": "randomization_test_no_measurement_validation",
                        },
                        {
                            "TransformVariantID": f"{sn_mode}__{bao_mode}",
                            "SubsetID": subset_id,
                            "ControlID": "EXACT_DEPTH_PERMUTATION_CONTROL",
                            "Rows": len(y),
                            "ObservedA2Chi2": observed,
                            "ControlCount": len(perm_scores),
                            "ControlMeanChi2": float(np.mean(perm_scores)),
                            "ControlMedianChi2": float(np.median(perm_scores)),
                            "ControlMinChi2": float(np.min(perm_scores)),
                            "EmpiricalP_ControlLEObserved": empirical_p_less_equal(perm_scores, observed),
                            "ObservedBeatsControlMedian": bool(observed < np.median(perm_scores)),
                            "ClaimBoundary": "randomization_test_no_measurement_validation",
                        },
                    ]
                )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (subset_id, control_id), group in detail.groupby(["SubsetID", "ControlID"], sort=False):
        summary_rows.append(
            {
                "SubsetID": subset_id,
                "ControlID": control_id,
                "TransformVariants": len(group),
                "ObservedBeatsControlMedianCount": int(group["ObservedBeatsControlMedian"].astype(bool).sum()),
                "MedianEmpiricalP_ControlLEObserved": float(group["EmpiricalP_ControlLEObserved"].median()),
                "MinEmpiricalP_ControlLEObserved": float(group["EmpiricalP_ControlLEObserved"].min()),
                "MaxEmpiricalP_ControlLEObserved": float(group["EmpiricalP_ControlLEObserved"].max()),
                "Interpretation": (
                    "a2_better_than_randomized_controls_in_most_variants"
                    if int(group["ObservedBeatsControlMedian"].astype(bool).sum()) >= len(group) // 2 + 1
                    else "a2_randomization_support_weak_or_mixed"
                ),
                "ClaimBoundary": "randomization_test_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
