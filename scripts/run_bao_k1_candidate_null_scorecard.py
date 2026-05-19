#!/usr/bin/env python3
"""Run null scorecard for the CMB-only unit-covnorm BAO K1 candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from numpy.linalg import solve

ROOT = Path(__file__).resolve().parents[1]
K1 = ROOT / "evidence" / "bao_k1_cmb_only_unit_covnorm_candidate.csv"
COV_SOURCE = ROOT / "evidence" / "bao_residual_transform_covariance.csv"
OUT = ROOT / "evidence" / "bao_k1_candidate_null_scorecard.csv"


def _covariance_for_product(product_id: str) -> np.ndarray:
    cov_df = pd.read_csv(COV_SOURCE)
    block = cov_df[cov_df["ProductID"] == product_id].copy()
    numeric = block.drop(columns=["ProductID", "CovRow"]).dropna(axis=1, how="all")
    return numeric.to_numpy(float)


def _chi2(y: np.ndarray, model: np.ndarray, cov: np.ndarray) -> float:
    residual = y - model
    return float(residual.T @ solve(cov, residual))


def _fit_poly(x: np.ndarray, y: np.ndarray, degree: int) -> np.ndarray:
    coeff = np.polyfit(x, y, degree)
    return np.polyval(coeff, x)


def main() -> None:
    df = pd.read_csv(K1)
    product_id = "DESI_DR2_BAO_ALL_GAUSSIAN"
    cov = _covariance_for_product(product_id)
    y = df["K1Response"].to_numpy(float)
    x = df["x_chi_normalized"].to_numpy(float)
    n = len(y)
    models = [
        ("ZERO_RESPONSE", np.zeros_like(y), 0, "fair_null"),
        ("CONSTANT_OFFSET", np.full_like(y, float(np.mean(y))), 1, "diagnostic_control"),
        ("POLY_DEG1", _fit_poly(x, y, 1), 2, "overfit_risk_control"),
        ("POLY_DEG2", _fit_poly(x, y, 2), 3, "overfit_risk_control"),
    ]
    rows = []
    for model_id, pred, k, category in models:
        c2 = _chi2(y, pred, cov)
        rows.append(
            {
                "ResponseTargetID": "BAO_K1_CMB_ONLY_UNIT_COVNORM_CANDIDATE",
                "ModelID": model_id,
                "NullCategory": category,
                "ParameterCount": k,
                "Chi2FullCov": c2,
                "AIC": c2 + 2 * k,
                "BIC": c2 + k * np.log(n),
                "Rows": n,
                "MappingID": "x_chi_normalized",
                "AllowedForK2Scoring": False,
                "Status": "K1_CANDIDATE_NULL_SCORECARD_ONLY",
            }
        )
    pd.DataFrame(rows).sort_values("AIC").to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
