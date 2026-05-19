#!/usr/bin/env python3
"""Run the registered-shrinkage future-preflight scorecard.

This consumes the registered shrinkage parameter policy. It is explicitly a
future-preflight scorecard, not a measurement-validation result.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

ACTIVATION = ROOT / "evidence" / "registered_shrinkage_activation_summary.csv"
PARAM_POLICY = ROOT / "evidence" / "registered_shrinkage_parameter_policy_readiness.csv"
PUBLIC_MARGINALS = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"

OUT_COV = ROOT / "evidence" / "registered_shrinkage_future_preflight_covariance.csv"
OUT_SCORECARD = ROOT / "evidence" / "registered_shrinkage_future_preflight_scorecard.csv"
OUT_SUMMARY = ROOT / "evidence" / "registered_shrinkage_future_preflight_summary.csv"


def bool_text(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sign_stable_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def model_rows(x: np.ndarray, y: np.ndarray, k1: np.ndarray) -> list[tuple[str, np.ndarray, int, str]]:
    models: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_RHO4", w_k2_locked(x, rho=4.0) * k1, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        models.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    return models


def build_covariance(x: np.ndarray, sigma: np.ndarray, lambda_shrink: float, corr_length: float) -> np.ndarray:
    distance = np.abs(x[:, None] - x[None, :])
    corr = lambda_shrink * np.exp(-distance / corr_length)
    np.fill_diagonal(corr, 1.0)
    return np.outer(sigma, sigma) * corr


def main() -> None:
    activation = pd.read_csv(ACTIVATION).iloc[0]
    if not bool_text(activation["RegisteredShrinkagePreflightActivationAllowed"]):
        raise SystemExit("registered shrinkage future-preflight activation is not allowed")

    policy = pd.read_csv(PARAM_POLICY).iloc[0]
    lambda_shrink = float(policy["PrimaryLambdaShrink"])
    corr_length = float(policy["PrimaryCorrelationLength"])
    rho_sn_bao = float(policy["PrimaryRhoSNBAO"])

    public = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    data = (
        external.merge(
            target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
            on="GridIndex",
            how="inner",
        )
        .merge(public, on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )

    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    sigma = data["SigmaPublicProxy"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()
    cov = build_covariance(x, sigma, lambda_shrink=lambda_shrink, corr_length=corr_length)
    cov = cov + np.eye(len(cov)) * 1e-12
    eig = np.linalg.eigvalsh(cov)

    cov_rows = []
    for i in range(len(data)):
        for j in range(len(data)):
            cov_rows.append(
                {
                    "CovarianceID": "REGISTERED_SHRINKAGE_FUTURE_PREFLIGHT_V1",
                    "RowI": i,
                    "RowJ": j,
                    "GridIndexI": int(data.loc[i, "GridIndex"]),
                    "GridIndexJ": int(data.loc[j, "GridIndex"]),
                    "x_i": float(x[i]),
                    "x_j": float(x[j]),
                    "SigmaI": float(sigma[i]),
                    "SigmaJ": float(sigma[j]),
                    "LambdaShrink": lambda_shrink,
                    "CorrelationLength": corr_length,
                    "RhoSNBAO": rho_sn_bao,
                    "Covariance": float(cov[i, j]),
                    "Correlation": float(cov[i, j] / (sigma[i] * sigma[j])),
                    "Status": "FUTURE_PREFLIGHT_ONLY",
                    "ClaimBoundary": "registered_shrinkage_future_preflight_no_measurement_validation",
                }
            )
    pd.DataFrame(cov_rows).to_csv(OUT_COV, index=False)

    score_rows = []
    for model_id, pred, parameter_count, model_class in model_rows(x, y, k1):
        c2 = chi2(y, pred, cov)
        score_rows.append(
            {
                "Dataset": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_REGISTERED_SHRINKAGE_FUTURE_PREFLIGHT",
                "CovarianceID": "REGISTERED_SHRINKAGE_FUTURE_PREFLIGHT_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": parameter_count,
                "Chi2": c2,
                "AIC": aic(c2, parameter_count),
                "BIC": bic(c2, parameter_count, len(y)),
                "SignStableViolations": sign_stable_violations(pred, y, stable),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "Status": "FUTURE_PREFLIGHT_ONLY",
                "ClaimBoundary": "registered_shrinkage_future_preflight_no_measurement_validation",
            }
        )
    scorecard = pd.DataFrame(score_rows)
    scorecard.to_csv(OUT_SCORECARD, index=False)

    best = scorecard.loc[scorecard["AIC"].idxmin()]
    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    k2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
    best_poly_aic = float(scorecard[scorecard["ModelID"].str.startswith("POLY")]["AIC"].min())
    summary = pd.DataFrame(
        [
            {
                "RunID": "REGISTERED_SHRINKAGE_FUTURE_PREFLIGHT_V1",
                "Rows": len(y),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly_aic,
                "LambdaShrink": lambda_shrink,
                "CorrelationLength": corr_length,
                "RhoSNBAO": rho_sn_bao,
                "MinEigenvalue": float(np.min(eig)),
                "MaxEigenvalue": float(np.max(eig)),
                "PositiveDefinite": bool(np.min(eig) > 0.0),
                "CurrentScorecardShouldRunNow": bool_text(activation["CurrentScorecardShouldRunNow"]),
                "AllowedRerunType": activation["AllowedRerunType"],
                "MeasurementValidationAllowed": False,
                "Interpretation": (
                    "registered_shrinkage_future_preflight_k2_competitive"
                    if k2_aic < best_poly_aic
                    else "registered_shrinkage_future_preflight_mixed_or_weakening"
                ),
                "ClaimBoundary": "registered_shrinkage_future_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
