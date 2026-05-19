#!/usr/bin/env python3
"""Score locked A2 on depth and memory-active subsets.

This keeps the prediction fixed and uses the existing public covariance proxy.
Polynomial controls are reported, but tiny subsets are marked as saturated or
underpowered rather than treated as measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
COV = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_memory_active_scorecard.csv"
SUMMARY = EVIDENCE / "k2_a2_memory_active_scorecard_summary.csv"


def chi2(y: np.ndarray, pred: np.ndarray, cov: np.ndarray) -> float:
    residual = y - pred
    return float(residual.T @ np.linalg.solve(cov, residual))


def aic(chi2_value: float, k: int) -> float:
    return float(chi2_value + 2 * k)


def bic(chi2_value: float, k: int, n: int) -> float:
    return float(chi2_value + k * np.log(n))


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def load_base() -> tuple[pd.DataFrame, np.ndarray]:
    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    cov_df = pd.read_csv(COV)
    data = (
        target[
            target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
            & target["SourceSplitResponse"].notna()
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

    indices = data["GridIndex"].astype(int).to_list()
    cov_rows = cov_df[cov_df["GridIndex"].astype(int).isin(indices)].sort_values("GridIndex")
    cov = cov_rows[[str(idx) for idx in indices]].to_numpy(float)
    cov = cov + np.eye(len(cov)) * 1e-12
    return data, cov


def subset_masks(data: pd.DataFrame) -> dict[str, np.ndarray]:
    zones = data["DepthZone"].astype(str).to_numpy()
    stable = data["SignStableBool"].astype(bool).to_numpy()
    same = data["SNBAOSameSignBool"].astype(bool).to_numpy()
    masks = {
        "all_depth": np.ones(len(data), dtype=bool),
        "low_depth": zones == "low_depth",
        "mid_depth": zones == "mid_depth",
        "high_depth": zones == "high_depth",
        "mid_high_memory_active": zones != "low_depth",
        "sign_stable_only": stable,
        "memory_active_sign_stable": (zones != "low_depth") & stable,
        "anti_aligned_only": ~same,
        "memory_active_anti_aligned": (zones != "low_depth") & (~same),
    }
    return {name: mask for name, mask in masks.items() if int(mask.sum()) > 0}


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray, unit: np.ndarray, a2_pred: np.ndarray):
    rows: list[tuple[str, np.ndarray, int, str, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null", "fixed"),
        ("K2_UNIT_LOCKED_RHO4", unit, 0, "locked_memory_backbone", "fixed"),
        ("K2_SOURCE_SPLIT_A2_PRIOR_V1", a2_pred, 0, "locked_projection_prior", "fixed"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control", "fixed"),
    ]
    for degree in [2, 3]:
        k = degree + 1
        if len(y) >= k:
            coeff = np.polyfit(x, y, degree)
            status = "saturated_or_tiny_subset" if len(y) <= k + 1 else "fit_control"
            rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), k, "overfit_risk_control", status))
        else:
            rows.append((f"POLY_DEG{degree}", np.full_like(y, np.nan), k, "overfit_risk_control", "not_enough_rows"))
    return rows


def main() -> None:
    data, cov_all = load_base()
    rows = []
    for subset_id, mask in subset_masks(data).items():
        idx = np.where(mask)[0]
        subset = data.loc[mask].copy()
        cov = cov_all[np.ix_(idx, idx)]
        y = subset["SourceSplitResponse"].to_numpy(float)
        x = subset["x_coordinate"].to_numpy(float)
        k1 = subset["K1Response"].to_numpy(float)
        unit = subset["K2UnitLockedRho4"].to_numpy(float)
        a2_pred = subset["K2SourceSplitA2Prediction"].to_numpy(float)
        stable = subset["SignStableBool"].to_numpy(bool)
        target_rms = rms(y)
        for model_id, pred_values, k, model_class, fit_status in model_rows(x, y, k1, unit, a2_pred):
            if np.isnan(pred_values).any():
                rows.append(
                    {
                        "SubsetID": subset_id,
                        "ModelID": model_id,
                        "ModelClass": model_class,
                        "Rows": len(y),
                        "ParameterCount": k,
                        "FitStatus": fit_status,
                        "Chi2": "",
                        "AIC": "",
                        "BIC": "",
                        "PredictionToTargetRMSRatio": "",
                        "MeanAbsResidual": "",
                        "SignStableViolations": "",
                        "SignMatchFraction": "",
                        "ClaimBoundary": "memory_active_scorecard_no_measurement_validation",
                    }
                )
                continue
            c2 = chi2(y, pred_values, cov)
            rows.append(
                {
                    "SubsetID": subset_id,
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(y),
                    "ParameterCount": k,
                    "FitStatus": fit_status,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "PredictionToTargetRMSRatio": rms(pred_values) / target_rms if target_rms > 0.0 else float("nan"),
                    "MeanAbsResidual": float(np.mean(np.abs(y - pred_values))),
                    "SignStableViolations": int(np.sum(np.sign(pred_values[stable]) != np.sign(y[stable]))),
                    "SignMatchFraction": float(np.mean(np.sign(pred_values) == np.sign(y))),
                    "ClaimBoundary": "memory_active_scorecard_no_measurement_validation",
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    summary_rows = []
    valid = output[pd.to_numeric(output["AIC"], errors="coerce").notna()].copy()
    valid["AIC"] = pd.to_numeric(valid["AIC"])
    for subset_id, group in valid.groupby("SubsetID", sort=False):
        a2_row = group[group["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")].iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        unit_row = group[group["ModelID"].eq("K2_UNIT_LOCKED_RHO4")].iloc[0]
        comparable_poly = group[
            group["ModelID"].str.startswith("POLY")
            & ~group["FitStatus"].astype(str).isin(["not_enough_rows"])
        ]
        if comparable_poly.empty:
            best_poly_id = "NONE"
            best_poly_aic = float("nan")
            a2_beats_poly = ""
            delta_poly = ""
            poly_warning = "no_polynomial_comparator_available"
        else:
            best_poly = comparable_poly.sort_values("AIC").iloc[0]
            best_poly_id = str(best_poly["ModelID"])
            best_poly_aic = float(best_poly["AIC"])
            a2_beats_poly = bool(float(a2_row["AIC"]) < best_poly_aic)
            delta_poly = float(a2_row["AIC"]) - best_poly_aic
            poly_warning = (
                "polynomial_saturated_or_tiny_subset"
                if str(best_poly["FitStatus"]) == "saturated_or_tiny_subset"
                else "polynomial_fit_control"
            )
        summary_rows.append(
            {
                "SubsetID": subset_id,
                "Rows": int(a2_row["Rows"]),
                "BestModel": str(group.sort_values("AIC").iloc[0]["ModelID"]),
                "A2AIC": float(a2_row["AIC"]),
                "K1AIC": float(k1_row["AIC"]),
                "UnitK2AIC": float(unit_row["AIC"]),
                "BestPolyModel": best_poly_id,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_A2_minus_K1": float(a2_row["AIC"]) - float(k1_row["AIC"]),
                "DeltaAIC_A2_minus_UnitK2": float(a2_row["AIC"]) - float(unit_row["AIC"]),
                "DeltaAIC_A2_minus_BestPoly": delta_poly,
                "A2ImprovesOverK1": bool(float(a2_row["AIC"]) < float(k1_row["AIC"])),
                "A2ImprovesOverUnitK2": bool(float(a2_row["AIC"]) < float(unit_row["AIC"])),
                "A2BeatsBestPoly": a2_beats_poly,
                "PolynomialComparisonWarning": poly_warning,
                "ClaimBoundary": "memory_active_scorecard_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
