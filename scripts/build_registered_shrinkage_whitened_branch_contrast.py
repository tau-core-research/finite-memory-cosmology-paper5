#!/usr/bin/env python3
"""Run the registered-shrinkage whitened branch-contrast preflight.

This is a declared covariance-route sensitivity check. It consumes the frozen
registered shrinkage parameter policy and applies the same standardized branch
contrast convention as WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1.
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
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"

OUT_VECTOR = ROOT / "evidence" / "registered_shrinkage_whitened_branch_contrast_vector.csv"
OUT_COV = ROOT / "evidence" / "registered_shrinkage_whitened_branch_contrast_covariance.csv"
OUT_SCORECARD = ROOT / "evidence" / "registered_shrinkage_whitened_branch_contrast_scorecard.csv"
OUT_SUMMARY = ROOT / "evidence" / "registered_shrinkage_whitened_branch_contrast_summary.csv"
OUT_DOC = ROOT / "docs" / "registered_shrinkage_whitened_branch_contrast.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def build_covariance(x: np.ndarray, sigma: np.ndarray, lambda_shrink: float, corr_length: float) -> np.ndarray:
    distance = np.abs(x[:, None] - x[None, :])
    corr = lambda_shrink * np.exp(-distance / corr_length)
    np.fill_diagonal(corr, 1.0)
    return np.outer(sigma, sigma) * corr


def inverse_sqrt_matrix(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigvals, eigvecs = np.linalg.eigh(0.5 * (covariance + covariance.T))
    if np.any(eigvals <= 0.0):
        raise ValueError(f"registered covariance is not positive definite: min={eigvals.min()}")
    whitening = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
    return eigvals, whitening


def weighted_poly_prediction(x: np.ndarray, y: np.ndarray, covariance: np.ndarray, degree: int) -> np.ndarray:
    design = np.vander(x, N=degree + 1, increasing=True)
    precision = np.linalg.inv(covariance)
    coeff = np.linalg.solve(design.T @ precision @ design, design.T @ precision @ y)
    return design @ coeff


def sign_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def main() -> None:
    activation = pd.read_csv(ACTIVATION).iloc[0]
    if not truthy(activation["RegisteredShrinkagePreflightActivationAllowed"]):
        raise SystemExit("registered shrinkage preflight activation is not allowed")

    policy = pd.read_csv(PARAM_POLICY).iloc[0]
    lambda_shrink = float(policy["PrimaryLambdaShrink"])
    corr_length = float(policy["PrimaryCorrelationLength"])
    rho_sn_bao = float(policy["PrimaryRhoSNBAO"])

    target = pd.read_csv(TARGET)
    k1_table = pd.read_csv(EXTERNAL_K1)
    marginals = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    data = (
        k1_table.merge(
            target[
                [
                    "GridIndex",
                    "z_grid",
                    "x_coordinate",
                    "SourceSplitResponse",
                    "SNStandardizedResidual",
                    "BAOStandardizedResidual",
                    "SignStableTemplate",
                    "HasSNAndBAO",
                ]
            ],
            on="GridIndex",
            how="inner",
        )
        .merge(marginals, on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data["z_grid"] = data["z_grid_y"] if "z_grid_y" in data.columns else data["z_grid"]
    data["x_coordinate"] = data["x_coordinate_y"] if "x_coordinate_y" in data.columns else data["x_coordinate"]

    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2 = w_k2_locked(x, rho=4.0) * k1
    sigma = data["SigmaPublicProxy"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    cov = build_covariance(x, sigma, lambda_shrink=lambda_shrink, corr_length=corr_length)
    cov = cov + np.eye(len(cov)) * 1e-12
    eigvals, whitening = inverse_sqrt_matrix(cov)
    y_white = whitening @ y

    poly2 = weighted_poly_prediction(x, y, cov, 2)
    poly3 = weighted_poly_prediction(x, y, cov, 3)
    models = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_RHO4", k2, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
        ("WEIGHTED_POLY_DEG2", poly2, 3, "overfit_risk_control"),
        ("WEIGHTED_POLY_DEG3", poly3, 4, "overfit_risk_control"),
    ]

    vector = data[
        [
            "GridIndex",
            "z_grid",
            "x_coordinate",
            "SNStandardizedResidual",
            "BAOStandardizedResidual",
            "SignStableTemplate",
            "SigmaPublicProxy",
        ]
    ].copy()
    vector.insert(0, "RunID", "REGISTERED_SHRINKAGE_WHITENED_BRANCH_CONTRAST_V1")
    vector["OriginalTarget"] = y
    vector["WhitenedTarget"] = y_white
    vector["K1Original"] = k1
    vector["K2LockedOriginal"] = k2
    vector["K1Whitened"] = whitening @ k1
    vector["K2LockedWhitened"] = whitening @ k2
    vector["LambdaShrink"] = lambda_shrink
    vector["CorrelationLength"] = corr_length
    vector["RhoSNBAO"] = rho_sn_bao
    vector["MeasurementValidationAllowed"] = False
    vector["ClaimBoundary"] = "registered_shrinkage_whitened_preflight_no_measurement_validation"
    vector.to_csv(OUT_VECTOR, index=False)

    cov_df = pd.DataFrame(cov, columns=[str(int(v)) for v in data["GridIndex"]])
    cov_df.insert(0, "GridIndex", data["GridIndex"].astype(int).to_list())
    cov_df.insert(0, "RunID", "REGISTERED_SHRINKAGE_WHITENED_BRANCH_CONTRAST_V1")
    cov_df["CovarianceEigenvalue"] = eigvals
    cov_df["PositiveDefinite"] = True
    cov_df["LambdaShrink"] = lambda_shrink
    cov_df["CorrelationLength"] = corr_length
    cov_df["ClaimBoundary"] = "registered_shrinkage_whitened_preflight_no_measurement_validation"
    cov_df.to_csv(OUT_COV, index=False)

    identity = np.eye(len(y))
    rows = []
    for model_id, pred, parameter_count, model_class in models:
        pred_white = whitening @ pred
        c2 = chi2(y, pred, cov)
        c2_white = chi2(y_white, pred_white, identity)
        rows.append(
            {
                "RunID": "REGISTERED_SHRINKAGE_WHITENED_BRANCH_CONTRAST_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": parameter_count,
                "Chi2": c2,
                "WhitenedIdentityChi2": c2_white,
                "Chi2ConsistencyAbsDiff": abs(c2 - c2_white),
                "AIC": aic(c2, parameter_count),
                "BIC": bic(c2, parameter_count, len(y)),
                "OriginalSignStableViolations": sign_violations(pred, y, stable),
                "WhitenedSignStableViolations": sign_violations(pred_white, y_white, stable),
                "MeanAbsWhitenedResidual": float(np.mean(np.abs(y_white - pred_white))),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "registered_shrinkage_whitened_preflight_no_measurement_validation",
            }
        )
    scorecard = pd.DataFrame(rows)
    k2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
    scorecard["DeltaAIC_vs_K2"] = scorecard["AIC"] - k2_aic
    scorecard.to_csv(OUT_SCORECARD, index=False)

    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    best_poly_aic = float(scorecard[scorecard["ModelID"].str.contains("POLY")]["AIC"].min())
    best = scorecard.loc[scorecard["AIC"].idxmin()]
    k2_improves_k1 = k2_aic < k1_aic
    k2_beats_poly = k2_aic < best_poly_aic
    summary = pd.DataFrame(
        [
            {
                "RunID": "REGISTERED_SHRINKAGE_WHITENED_BRANCH_CONTRAST_V1",
                "Rows": len(y),
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_improves_k1,
                "K2BeatsBestPoly": k2_beats_poly,
                "LambdaShrink": lambda_shrink,
                "CorrelationLength": corr_length,
                "RhoSNBAO": rho_sn_bao,
                "CovarianceMinEigenvalue": float(np.min(eigvals)),
                "CovarianceMaxEigenvalue": float(np.max(eigvals)),
                "PositiveDefinite": bool(np.min(eigvals) > 0.0),
                "RegisteredBeforeThisScore": True,
                "LockedA2Changed": False,
                "K1Refit": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "REGISTERED_SHRINKAGE_WHITENED_PREFLIGHT_SUPPORTIVE"
                    if k2_improves_k1 and k2_beats_poly
                    else "REGISTERED_SHRINKAGE_WHITENED_PREFLIGHT_MIXED_OR_WEAKENING"
                ),
                "StrongestAllowedClaim": (
                    "registered shrinkage whitening is executable as a preflight covariance route without changing locked A2/K2"
                ),
                "PrimaryResidualRisk": (
                    "registered shrinkage is not a public full joint covariance and cannot authorize measurement validation"
                ),
                "NextAction": (
                    "compare against the public-proxy whitened result and keep both outcomes reported before any public likelihood-native benchmark"
                ),
                "ClaimBoundary": "registered_shrinkage_whitened_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Registered Shrinkage Whitened Branch Contrast",
                "",
                "Status: preflight covariance-route sensitivity; no measurement-validation claim.",
                "",
                "This run applies the pre-registered shrinkage covariance route to the standardized SN-BAO branch contrast. It keeps the locked K2 kernel and frozen K1 baseline unchanged.",
                "",
                "## Outputs",
                "",
                f"- Vector: `{OUT_VECTOR.relative_to(ROOT)}`",
                f"- Covariance: `{OUT_COV.relative_to(ROOT)}`",
                f"- Scorecard: `{OUT_SCORECARD.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "The route is useful for covariance sensitivity, but it is not a substitute for a public full SN-BAO joint covariance.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_VECTOR}")
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
