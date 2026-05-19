#!/usr/bin/env python3
"""Cross-covariance sensitivity for A2 memory-active subsets.

This uses the frozen exported L_SN/L_BAO transforms and the locked A2
prediction. The row-aligned cross-covariance grid is sensitivity-only; no
rho_cross value is selected to rescue any model.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.public_data import load_flat_covariance_with_size

EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
SN_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_COV = EVIDENCE / "bao_residual_transform_covariance.csv"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"

OUT = EVIDENCE / "k2_a2_memory_active_cross_covariance.csv"
SUMMARY = EVIDENCE / "k2_a2_memory_active_cross_covariance_summary.csv"


def load_transform(path: Path) -> tuple[list[int], np.ndarray]:
    df = pd.read_csv(path)
    return df["GridIndex"].astype(int).to_list(), df.drop(columns=["GridIndex"]).to_numpy(float)


def load_bao_covariance(path: Path) -> np.ndarray:
    rows = pd.read_csv(path)
    rows = rows[rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].sort_values("CovRow")
    value_cols = [col for col in rows.columns if col not in {"ProductID", "CovRow"}]
    return rows[value_cols].to_numpy(float)


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def chi2(y: np.ndarray, pred: np.ndarray, cov: np.ndarray) -> float:
    residual = y - pred
    return float(residual.T @ np.linalg.solve(cov, residual))


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
        for degree in [2, 3]:
            coeff = np.polyfit(x, y, degree)
            rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    elif len(y) >= 3:
        coeff = np.polyfit(x, y, 2)
        rows.append(("POLY_DEG2", np.polyval(coeff, x), 3, "overfit_risk_control_saturated"))
    return rows


def subset_masks(data: pd.DataFrame) -> dict[str, np.ndarray]:
    zones = data["DepthZone"].astype(str).to_numpy()
    stable = data["SignStableBool"].astype(bool).to_numpy()
    same = data["SNBAOSameSignBool"].astype(bool).to_numpy()
    masks = {
        "all_depth": np.ones(len(data), dtype=bool),
        "mid_high_memory_active": zones != "low_depth",
        "high_depth": zones == "high_depth",
        "memory_active_sign_stable": (zones != "low_depth") & stable,
        "memory_active_anti_aligned": (zones != "low_depth") & (~same),
    }
    return {key: value for key, value in masks.items() if int(value.sum()) >= 3}


def cross_covariance(sn_cov: np.ndarray, bao_cov: np.ndarray, rho_cross: float) -> np.ndarray:
    sn_sigma = np.sqrt(np.maximum(np.diag(sn_cov), 0.0))
    bao_sigma = np.sqrt(np.maximum(np.diag(bao_cov), 0.0))
    cross = np.diag(float(rho_cross) * sn_sigma * bao_sigma)
    return sn_cov + bao_cov - cross - cross.T


def positive_definite(cov: np.ndarray) -> bool:
    try:
        np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        return False
    return True


def main() -> None:
    sn_grid, l_sn = load_transform(L_SN)
    bao_grid, l_bao = load_transform(L_BAO)
    if sn_grid != bao_grid:
        raise ValueError("SN and BAO transform grids differ")

    sn_cov_raw = load_flat_covariance_with_size(SN_COV)
    bao_cov_raw = load_bao_covariance(BAO_COV)
    sn_cov = l_sn @ sn_cov_raw @ l_sn.T
    bao_cov = l_bao @ bao_cov_raw @ l_bao.T

    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    data = (
        target[
            target["GridIndex"].astype(int).isin(sn_grid)
            & target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
        ][["GridIndex", "z_grid", "x_coordinate", "SourceSplitResponse", "SignStableTemplate", "SNBAOSameSign"]]
        .merge(
            pred[
                [
                    "GridIndex",
                    "K1Response",
                    "K2UnitLockedRho4",
                    "K2SourceSplitA2Prediction",
                ]
            ],
            on="GridIndex",
            how="inner",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data["DepthZone"] = [depth_zone(float(x)) for x in data["x_coordinate"]]
    data["SignStableBool"] = data["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    data["SNBAOSameSignBool"] = data["SNBAOSameSign"].astype(str).str.lower().isin(["true", "1", "yes"])

    grid_to_pos = {grid: pos for pos, grid in enumerate(sn_grid)}
    full_positions = [grid_to_pos[int(idx)] for idx in data["GridIndex"]]
    sn_cov = sn_cov[np.ix_(full_positions, full_positions)]
    bao_cov = bao_cov[np.ix_(full_positions, full_positions)]

    rho_values = np.round(np.linspace(-0.9, 0.4, 27), 3)
    rows = []
    for rho_cross in rho_values:
        cov_full = cross_covariance(sn_cov, bao_cov, float(rho_cross)) + np.eye(len(data)) * 1e-12
        if not positive_definite(cov_full):
            continue
        for subset_id, mask in subset_masks(data).items():
            idx = np.where(mask)[0]
            subset = data.loc[mask].copy()
            cov = cov_full[np.ix_(idx, idx)]
            y = subset["SourceSplitResponse"].to_numpy(float)
            x = subset["x_coordinate"].to_numpy(float)
            k1 = subset["K1Response"].to_numpy(float)
            unit = subset["K2UnitLockedRho4"].to_numpy(float)
            a2_pred = subset["K2SourceSplitA2Prediction"].to_numpy(float)
            for model_id, values, k, model_class in model_rows(x, y, k1, unit, a2_pred):
                c2 = chi2(y, values, cov)
                rows.append(
                    {
                        "RhoCross": float(rho_cross),
                        "SubsetID": subset_id,
                        "ModelID": model_id,
                        "ModelClass": model_class,
                        "Rows": len(y),
                        "ParameterCount": k,
                        "Chi2": c2,
                        "AIC": aic(c2, k),
                        "ClaimBoundary": "memory_active_cross_covariance_no_measurement_validation",
                    }
                )
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (rho_cross, subset_id), group in detail.groupby(["RhoCross", "SubsetID"], sort=True):
        a2_row = group[group["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")].iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        unit_row = group[group["ModelID"].eq("K2_UNIT_LOCKED_RHO4")].iloc[0]
        poly = group[group["ModelID"].str.startswith("POLY")]
        best_poly_aic = float(poly["AIC"].min()) if not poly.empty else float("nan")
        best_model = group.sort_values("AIC").iloc[0]
        summary_rows.append(
            {
                "RhoCross": float(rho_cross),
                "SubsetID": subset_id,
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
                "ClaimBoundary": "memory_active_cross_covariance_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
