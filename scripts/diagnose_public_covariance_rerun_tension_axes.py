#!/usr/bin/env python3
"""Diagnose tension axes in the public-covariance locked-A2 rerun.

The script isolates whether the mixed/weakening rerun is driven mainly by
sign, scale, depth zone, local A_tau demand, or polynomial shape flexibility.
All alternative scores are counterfactual diagnostics only; locked A2 remains
unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2

EVIDENCE = ROOT / "evidence"

VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COVARIANCE = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
WEAKENING_AUDIT = EVIDENCE / "likelihood_native_rerun_weakening_audit.csv"

OUT_AUDIT = EVIDENCE / "public_covariance_rerun_tension_axes_audit.csv"
OUT_SUMMARY = EVIDENCE / "public_covariance_rerun_tension_axes_summary.csv"


def depth_zone(x: float) -> str:
    if x < 0.5:
        return "low_depth"
    if x < 0.8:
        return "mid_depth"
    return "high_depth"


def load_covariance(vector: pd.DataFrame) -> np.ndarray:
    cov = pd.read_csv(COVARIANCE)
    grid = [str(int(v)) for v in vector["GridIndex"]]
    return cov[grid].to_numpy(float)


def safe_div(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    out = np.full_like(num, np.nan, dtype=float)
    mask = np.abs(den) > 1e-12
    out[mask] = num[mask] / den[mask]
    return out


def subset_score(
    subset_id: str,
    mask: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    cov: np.ndarray,
    models: dict[str, tuple[np.ndarray, int, str]],
) -> list[dict[str, object]]:
    if int(mask.sum()) < 2:
        return []
    idx = np.where(mask)[0]
    cov_sub = cov[np.ix_(idx, idx)]
    rows = []
    for model_id, (pred, k, model_class) in models.items():
        y_sub = y[idx]
        pred_sub = pred[idx]
        c2 = chi2(y_sub, pred_sub, cov_sub)
        rows.append(
            {
                "SummaryID": f"SUBSET_{subset_id}",
                "SubsetID": subset_id,
                "Rows": len(idx),
                "ModelID": model_id,
                "ModelClass": model_class,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(idx)),
                "ParameterCount": k,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "public_covariance_rerun_tension_axes_no_measurement_validation",
            }
        )
    return rows


def main() -> None:
    vector = pd.read_csv(VECTOR).sort_values("GridIndex").reset_index(drop=True)
    weakening = pd.read_csv(WEAKENING_AUDIT).sort_values("GridIndex").reset_index(drop=True)
    cov = load_covariance(vector)

    x = vector["x_coordinate"].to_numpy(float)
    y = vector["SourceSplitCandidate"].to_numpy(float)
    k1 = vector["K1Response"].to_numpy(float)
    k2 = vector["K2LockedA2Prediction"].to_numpy(float)
    sigma = np.sqrt(vector["CovarianceDiag"].to_numpy(float))
    w_depth = safe_div(k2, k1)
    local_a_tau = safe_div(y, k2 / 2.0)

    poly2_coeff = np.polyfit(x, y, 2)
    poly3_coeff = np.polyfit(x, y, 3)
    poly2 = np.polyval(poly2_coeff, x)
    poly3 = np.polyval(poly3_coeff, x)

    models = {
        "K1_NO_MEMORY": (k1, 0, "fair_null"),
        "K2_LOCKED_A2_UNCHANGED": (k2, 0, "locked_prediction"),
        "POLY_DEG2": (poly2, 3, "overfit_risk_control"),
        "POLY_DEG3": (poly3, 4, "overfit_risk_control"),
    }

    denom = float(k2.T @ np.linalg.solve(cov, k2))
    beta_full = float(k2.T @ np.linalg.solve(cov, y) / denom) if denom > 0 else np.nan
    beta_diag = float(np.sum(y * k2 / (sigma * sigma)) / np.sum(k2 * k2 / (sigma * sigma)))
    k2_beta_full = beta_full * k2
    k2_beta_diag = beta_diag * k2
    k2_sign_aligned = np.sign(y) * np.abs(k2)

    audit = vector[
        [
            "GridIndex",
            "z_grid",
            "x_coordinate",
            "SourceSplitCandidate",
            "K1Response",
            "K2LockedA2Prediction",
            "CovarianceDiag",
        ]
    ].copy()
    audit["DepthZone"] = [depth_zone(v) for v in x]
    audit["SigmaDiag"] = sigma
    audit["DepthMultiplierK2OverK1"] = w_depth
    audit["LocalATauRequiredForTarget"] = local_a_tau
    audit["AbsLocalATauRequired"] = np.abs(local_a_tau)
    audit["K2TargetSignMismatch"] = np.sign(y) != np.sign(k2)
    audit["K1TargetSignMismatch"] = np.sign(y) != np.sign(k1)
    audit["K2OvershootsAbsTarget"] = np.abs(k2) > np.abs(y)
    audit["K2AbsOverTargetAbs"] = safe_div(np.abs(k2), np.abs(y))
    audit["TargetAbsOverK2Abs"] = safe_div(np.abs(y), np.abs(k2))
    audit["ResidualK1OverSigma"] = (y - k1) / sigma
    audit["ResidualK2OverSigma"] = (y - k2) / sigma
    audit["ResidualSignAlignedK2OverSigma"] = (y - k2_sign_aligned) / sigma
    audit["ResidualBetaFullK2OverSigma"] = (y - k2_beta_full) / sigma
    audit["ResidualBetaDiagK2OverSigma"] = (y - k2_beta_diag) / sigma
    audit["WeakeningMechanism"] = weakening["WeakeningMechanism"]

    tension_axis = []
    for _, row in audit.iterrows():
        axes: list[str] = []
        if row["K2TargetSignMismatch"]:
            axes.append("SIGN_AXIS")
        if row["K2OvershootsAbsTarget"]:
            axes.append("AMPLITUDE_OVERSHOOT_AXIS")
        if np.isfinite(row["LocalATauRequiredForTarget"]) and row["AbsLocalATauRequired"] < 1.0:
            axes.append("TARGET_SCALE_BELOW_LOCKED_A2_AXIS")
        if "flexible_polynomial" in str(row["WeakeningMechanism"]):
            axes.append("SHAPE_FLEXIBILITY_AXIS")
        if not axes:
            axes.append("MINOR_OR_COVARIANCE_COUPLED_AXIS")
        tension_axis.append(";".join(axes))
    audit["PrimaryTensionAxes"] = tension_axis
    audit["MeasurementValidationAllowed"] = False
    audit["ClaimBoundary"] = "public_covariance_rerun_tension_axes_no_measurement_validation"
    audit.to_csv(OUT_AUDIT, index=False)

    extended_models = dict(models)
    extended_models["K2_COUNTERFACTUAL_BETA_FULL"] = (k2_beta_full, 1, "diagnostic_counterfactual")
    extended_models["K2_COUNTERFACTUAL_BETA_DIAG"] = (k2_beta_diag, 1, "diagnostic_counterfactual")
    extended_models["K2_COUNTERFACTUAL_SIGN_ALIGNED"] = (k2_sign_aligned, 0, "diagnostic_counterfactual")

    masks = {
        "all": np.ones(len(vector), dtype=bool),
        "sign_match": np.sign(y) == np.sign(k2),
        "sign_mismatch": np.sign(y) != np.sign(k2),
        "k2_overshoot": np.abs(k2) > np.abs(y),
        "no_k2_overshoot": np.abs(k2) <= np.abs(y),
        "low_depth": np.array([depth_zone(v) == "low_depth" for v in x]),
        "mid_depth": np.array([depth_zone(v) == "mid_depth" for v in x]),
        "high_depth": np.array([depth_zone(v) == "high_depth" for v in x]),
        "mid_high": np.array([depth_zone(v) in {"mid_depth", "high_depth"} for v in x]),
    }

    summary_rows: list[dict[str, object]] = [
        {
            "SummaryID": "TENSION_AXES_OVERVIEW",
            "Rows": len(vector),
            "K2SignMismatchRows": int(np.sum(np.sign(y) != np.sign(k2))),
            "K1SignMismatchRows": int(np.sum(np.sign(y) != np.sign(k1))),
            "K2OvershootRows": int(np.sum(np.abs(k2) > np.abs(y))),
            "MedianAbsLocalATauRequired": float(np.nanmedian(np.abs(local_a_tau))),
            "MeanAbsLocalATauRequired": float(np.nanmean(np.abs(local_a_tau))),
            "BetaFullCovarianceBestK2Scale": beta_full,
            "BetaDiagonalBestK2Scale": beta_diag,
            "LockedScale": 1.0,
            "CounterfactualOnly": True,
            "MeasurementValidationAllowed": False,
            "CurrentStatus": "PUBLIC_RERUN_TENSION_AXES_DIAGNOSED_NO_A2_CHANGE_AUTHORIZED",
            "StrongestAllowedClaim": "the public-covariance rerun tension is mostly sign/scale/shape-axis driven under the candidate target",
            "NextAction": "test whether sign and scale axes come from target construction or from genuine A2 mismatch; keep locked A2 unchanged",
            "ClaimBoundary": "public_covariance_rerun_tension_axes_no_measurement_validation",
        }
    ]
    for subset_id, mask in masks.items():
        summary_rows.extend(subset_score(subset_id, mask, x, y, cov, extended_models))

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
