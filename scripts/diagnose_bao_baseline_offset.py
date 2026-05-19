#!/usr/bin/env python3
"""Diagnose the constant-offset mode in the T1 BAO residual preflight."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "evidence" / "bao_residual_transform_preflight.csv"
COV = ROOT / "evidence" / "bao_residual_transform_covariance.csv"
OUT = ROOT / "evidence" / "bao_baseline_offset_diagnosis.csv"

AUDIT_RD_MPC = 147.0


def _covariance_for_product(product_id: str) -> np.ndarray:
    cov_df = pd.read_csv(COV)
    block = cov_df[cov_df["ProductID"] == product_id].copy()
    if block.empty:
        raise ValueError(f"missing covariance block for {product_id}")
    numeric = block.drop(columns=["ProductID", "CovRow"])
    numeric = numeric.dropna(axis=1, how="all")
    cov = numeric.to_numpy(float)
    if cov.shape[0] != cov.shape[1]:
        raise ValueError(f"covariance block is not square for {product_id}: {cov.shape}")
    return cov


def _weighted_constant_offset(y: np.ndarray, cov: np.ndarray) -> tuple[float, float]:
    inv = np.linalg.inv(cov)
    ones = np.ones_like(y)
    denom = float(ones.T @ inv @ ones)
    offset = float((ones.T @ inv @ y) / denom)
    sigma = float(np.sqrt(1.0 / denom))
    return offset, sigma


def _chi2(y: np.ndarray, model: np.ndarray, cov: np.ndarray) -> float:
    residual = y - model
    return float(residual.T @ np.linalg.solve(cov, residual))


def main() -> None:
    df = pd.read_csv(ROWS)
    out_rows = []

    for product_id, block in df.groupby("ProductID", sort=True):
        y = block["LogResidual"].to_numpy(float)
        cov = _covariance_for_product(product_id)
        offset, sigma = _weighted_constant_offset(y, cov)
        zero_model = np.zeros_like(y)
        offset_model = np.full_like(y, offset)
        chi2_zero = _chi2(y, zero_model, cov)
        chi2_offset = _chi2(y, offset_model, cov)

        # Prediction is distance / rd. A positive log residual means observed is
        # larger than the audit prediction, so the equivalent rd is smaller.
        scale_factor = float(np.exp(offset))
        effective_rd = float(AUDIT_RD_MPC / scale_factor)

        out_rows.append(
            {
                "ProductID": product_id,
                "Rows": len(block),
                "WeightedLogOffset": offset,
                "WeightedLogOffsetSigma": sigma,
                "OffsetOverSigma": offset / sigma if sigma > 0 else np.nan,
                "ObservedOverAuditScale": scale_factor,
                "AuditRdMpc": AUDIT_RD_MPC,
                "EffectiveRdMpcIfAbsorbed": effective_rd,
                "Chi2ZeroResidual": chi2_zero,
                "Chi2ConstantOffset": chi2_offset,
                "DeltaChi2OffsetVsZero": chi2_offset - chi2_zero,
                "Interpretation": "audit_baseline_scale_offset_not_finite_memory_signal",
                "AllowedForMeasurementGate": False,
                "NextAction": "replace audit-fiducial baseline with likelihood-native or coordinate-native BAO baseline export",
            }
        )

    pd.DataFrame(out_rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
