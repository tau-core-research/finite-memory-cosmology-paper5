#!/usr/bin/env python3
"""Build and score the residual-policy rerun candidate.

This rerun uses the frozen residual policies, the declared L_SN/L_BAO matrices,
and the locked A2 prediction unchanged. It is a candidate preflight rerun, not
measurement validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.public_data import load_flat_covariance_with_size, load_square_covariance

DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"

SN_RESID = DATA / "residuals" / "sn_cmb_only_raw_residual_v1.csv"
BAO_RESID = DATA / "residuals" / "bao_cmb_only_log_residual_v1.csv"
SN_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_COV = DATA / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
K2 = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT_VECTOR = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
OUT_COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
OUT_SCORE = EVIDENCE / "likelihood_native_rerun_candidate_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "likelihood_native_rerun_candidate_summary.csv"


def load_transform(path: Path) -> tuple[list[int], np.ndarray]:
    df = pd.read_csv(path)
    grid = df["GridIndex"].astype(int).to_list()
    matrix = df.drop(columns=["GridIndex"]).to_numpy(float)
    return grid, matrix


def bao_log_covariance(bao_residual: pd.DataFrame, bao_covariance: np.ndarray) -> np.ndarray:
    observed = bao_residual["ObservedValue"].to_numpy(float)
    jac = np.diag(1.0 / observed)
    return jac @ np.asarray(bao_covariance, dtype=float) @ jac


def positive_definite(cov: np.ndarray) -> tuple[bool, float, float]:
    eig = np.linalg.eigvalsh(np.asarray(cov, dtype=float))
    return bool(float(np.min(eig)) > 0.0), float(np.min(eig)), float(np.max(eig))


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray, k2: np.ndarray) -> list[tuple[str, np.ndarray, int, str]]:
    rows: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_A2_UNCHANGED", k2, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    return rows


def main() -> None:
    sn_grid, l_sn = load_transform(L_SN)
    bao_grid, l_bao = load_transform(L_BAO)
    if sn_grid != bao_grid:
        raise ValueError("L_SN and L_BAO grid mismatch")

    sn = pd.read_csv(SN_RESID)
    bao = pd.read_csv(BAO_RESID)
    sn_cov = load_flat_covariance_with_size(SN_COV)
    bao_cov = bao_log_covariance(bao, load_square_covariance(BAO_COV))

    r_sn = sn["RawResidualMu"].to_numpy(float)
    r_bao = bao["LogResidual"].to_numpy(float)
    y_split = l_sn @ r_sn - l_bao @ r_bao
    cov_split = l_sn @ sn_cov @ l_sn.T + l_bao @ bao_cov @ l_bao.T
    cov_split = cov_split + np.eye(len(cov_split)) * 1e-12
    pd_ok, eig_min, eig_max = positive_definite(cov_split)

    k1 = pd.read_csv(K1).set_index("GridIndex")
    k2 = pd.read_csv(K2).set_index("GridIndex")
    rows = []
    for idx, y_value in zip(sn_grid, y_split):
        rows.append(
            {
                "CandidateID": "LIKELIHOOD_NATIVE_RERUN_CANDIDATE_V1",
                "GridIndex": idx,
                "z_grid": float(k1.loc[idx, "z_grid"]),
                "x_coordinate": float(k1.loc[idx, "x_coordinate"]),
                "SourceSplitCandidate": float(y_value),
                "K1Response": float(k1.loc[idx, "K1Response"]),
                "K2LockedA2Prediction": float(k2.loc[idx, "K2SourceSplitA2Prediction"]),
                "CovarianceDiag": float(cov_split[sn_grid.index(idx), sn_grid.index(idx)]),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "likelihood_native_rerun_candidate_no_measurement_validation",
            }
        )
    vector = pd.DataFrame(rows)
    vector.to_csv(OUT_VECTOR, index=False)

    cov_df = pd.DataFrame(cov_split, columns=[str(idx) for idx in sn_grid])
    cov_df.insert(0, "GridIndex", sn_grid)
    cov_df.insert(0, "CovarianceID", "LIKELIHOOD_NATIVE_RERUN_CANDIDATE_ZERO_CROSS_V1")
    cov_df["PositiveDefinite"] = pd_ok
    cov_df["MeasurementValidationAllowed"] = False
    cov_df["ClaimBoundary"] = "likelihood_native_rerun_candidate_no_measurement_validation"
    cov_df.to_csv(OUT_COV, index=False)

    x = vector["x_coordinate"].to_numpy(float)
    y = vector["SourceSplitCandidate"].to_numpy(float)
    k1_pred = vector["K1Response"].to_numpy(float)
    k2_pred = vector["K2LockedA2Prediction"].to_numpy(float)
    score_rows = []
    for model_id, pred, k, model_class in model_rows(x, y, k1_pred, k2_pred):
        c2 = chi2(y, pred, cov_split)
        score_rows.append(
            {
                "CandidateID": "LIKELIHOOD_NATIVE_RERUN_CANDIDATE_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "likelihood_native_rerun_candidate_no_measurement_validation",
            }
        )
    score = pd.DataFrame(score_rows)
    score.to_csv(OUT_SCORE, index=False)

    k1_aic = float(score.loc[score["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    k2_aic = float(score.loc[score["ModelID"].eq("K2_LOCKED_A2_UNCHANGED"), "AIC"].iloc[0])
    best_poly_aic = float(score[score["ModelID"].str.startswith("POLY")]["AIC"].min())
    best = score.loc[score["AIC"].idxmin()]
    summary = pd.DataFrame(
        [
            {
                "CandidateID": "LIKELIHOOD_NATIVE_RERUN_CANDIDATE_V1",
                "Rows": len(vector),
                "CovariancePositiveDefinite": pd_ok,
                "CovarianceMinEigenvalue": eig_min,
                "CovarianceMaxEigenvalue": eig_max,
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly_aic,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "LOCKED_A2_RERUN_CANDIDATE_SUPPORTIVE"
                    if k2_aic < k1_aic and k2_aic < best_poly_aic
                    else "LOCKED_A2_RERUN_CANDIDATE_MIXED_OR_WEAKENING"
                ),
                "StrongestAllowedClaim": "locked A2 has been rerun on the frozen residual-policy candidate route",
                "PrimaryResidualRisk": "candidate route still uses declared zero-cross covariance and is not measurement validation",
                "ClaimBoundary": "likelihood_native_rerun_candidate_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_VECTOR}")
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
