#!/usr/bin/env python3
"""Build the CMB-only unit-covnorm BAO K1 response candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from numpy.linalg import solve

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evidence" / "cmb_only_bao_baseline_export.csv"
COV_SOURCE = ROOT / "evidence" / "bao_residual_transform_covariance.csv"
OUT = ROOT / "evidence" / "bao_k1_cmb_only_unit_covnorm_candidate.csv"
OUT_SUMMARY = ROOT / "evidence" / "bao_k1_cmb_only_unit_covnorm_summary.csv"


def _covariance_for_product(product_id: str) -> np.ndarray:
    cov_df = pd.read_csv(COV_SOURCE)
    block = cov_df[cov_df["ProductID"] == product_id].copy()
    numeric = block.drop(columns=["ProductID", "CovRow"]).dropna(axis=1, how="all")
    cov = numeric.to_numpy(float)
    if cov.shape[0] != cov.shape[1]:
        raise ValueError(f"covariance block is not square for {product_id}: {cov.shape}")
    return cov


def main() -> None:
    df = pd.read_csv(SOURCE)
    product_id = "DESI_DR2_BAO_ALL_GAUSSIAN"
    block = df[df["ProductID"] == product_id].copy().reset_index(drop=True)
    cov = _covariance_for_product(product_id)
    residual = block["LogResidual"].to_numpy(float)
    cov_norm = float(np.sqrt(residual.T @ solve(cov, residual)))
    if cov_norm <= 0.0:
        raise ValueError("CMB-only residual has zero covariance norm")
    k1 = residual / cov_norm
    block["K1Response"] = k1
    block["OriginalResidual"] = residual
    block["UnitCovarianceNorm"] = cov_norm
    block["ResponseTargetID"] = "BAO_K1_CMB_ONLY_UNIT_COVNORM_CANDIDATE"
    block["AmplitudeNormalization"] = "unit_covariance_norm"
    block["AllowedForK2Scoring"] = False
    block["ClaimBoundary"] = "candidate_only_not_k2_scoring"
    block.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "ResponseTargetID": "BAO_K1_CMB_ONLY_UNIT_COVNORM_CANDIDATE",
                "ProductID": product_id,
                "Rows": len(block),
                "SourceBaseline": "CMB_ONLY_BASE_PLANCK_ACT_LENSING_IMINUIT_BESTFIT_V0",
                "CovarianceNormBeforeNormalization": cov_norm,
                "CovarianceNormAfterNormalization": float(k1.T @ solve(cov, k1)),
                "MeanAbsK1Response": float(np.mean(np.abs(k1))),
                "MaxAbsK1Response": float(np.max(np.abs(k1))),
                "AllowedForK2Scoring": False,
                "BlockingIssue": "candidate_not_selected;null_scorecard_required;k2_protocol_not_ready",
                "Interpretation": "independent_cmb_only_k1_candidate_not_measurement_gate",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
