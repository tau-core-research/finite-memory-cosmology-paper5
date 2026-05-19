#!/usr/bin/env python3
"""Build the whitened standardized branch-contrast preflight target.

This implements WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1 as a preflight
measurement-candidate convention. It keeps the locked A2/K2 operator unchanged,
does not refit K1, and does not authorize measurement validation.
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

TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
PUBLIC_COV = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy.csv"

OUT_VECTOR = ROOT / "evidence" / "whitened_standardized_branch_contrast_vector.csv"
OUT_MATRIX = ROOT / "evidence" / "whitened_standardized_branch_contrast_matrix.csv"
OUT_SCORECARD = ROOT / "evidence" / "whitened_standardized_branch_contrast_scorecard.csv"
OUT_SUMMARY = ROOT / "evidence" / "whitened_standardized_branch_contrast_summary.csv"
OUT_DOC = ROOT / "docs" / "whitened_standardized_branch_contrast.md"


def load_covariance() -> tuple[list[int], np.ndarray]:
    cov_rows = pd.read_csv(PUBLIC_COV)
    grid_indices = cov_rows["GridIndex"].astype(int).to_list()
    value_cols = [str(idx) for idx in grid_indices]
    cov = cov_rows[value_cols].to_numpy(float)
    cov = 0.5 * (cov + cov.T)
    return grid_indices, cov


def inverse_sqrt_matrix(covariance: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    eigvals, eigvecs = np.linalg.eigh(covariance)
    if np.any(eigvals <= 0.0):
        raise ValueError(f"covariance is not positive definite: min eigenvalue={eigvals.min()}")
    whitening = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
    return eigvals, whitening


def weighted_poly_prediction(x: np.ndarray, y: np.ndarray, covariance: np.ndarray, degree: int) -> np.ndarray:
    design = np.vander(x, N=degree + 1, increasing=True)
    precision = np.linalg.inv(covariance)
    normal = design.T @ precision @ design
    rhs = design.T @ precision @ y
    coeff = np.linalg.solve(normal, rhs)
    return design @ coeff


def sign_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    mask = stable.astype(bool)
    if not np.any(mask):
        return 0
    return int(np.sum(np.sign(pred[mask]) != np.sign(y[mask])))


def main() -> None:
    target = pd.read_csv(TARGET)
    k1_table = pd.read_csv(EXTERNAL_K1)
    grid_indices, cov = load_covariance()

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
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data = data[data["GridIndex"].isin(grid_indices)].copy()
    data["GridIndex"] = pd.Categorical(data["GridIndex"], categories=grid_indices, ordered=True)
    data = data.sort_values("GridIndex").reset_index(drop=True)

    # Use the declared target coordinate after merge; the external K1 export may
    # carry its own nearby coordinate as provenance metadata.
    data["z_grid"] = data["z_grid_y"] if "z_grid_y" in data.columns else data["z_grid"]
    data["x_coordinate"] = data["x_coordinate_y"] if "x_coordinate_y" in data.columns else data["x_coordinate"]
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2 = w_k2_locked(x, rho=4.0) * k1
    zero = np.zeros_like(y)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    eigvals, whitening = inverse_sqrt_matrix(cov)
    y_white = whitening @ y
    k1_white = whitening @ k1
    k2_white = whitening @ k2
    zero_white = whitening @ zero
    poly2 = weighted_poly_prediction(x, y, cov, 2)
    poly3 = weighted_poly_prediction(x, y, cov, 3)
    poly2_white = whitening @ poly2
    poly3_white = whitening @ poly3

    vector = data[
        [
            "GridIndex",
            "z_grid",
            "x_coordinate",
            "SNStandardizedResidual",
            "BAOStandardizedResidual",
            "SignStableTemplate",
        ]
    ].copy()
    vector.insert(0, "TargetConventionID", "WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1")
    vector["OriginalTarget"] = y
    vector["K1Original"] = k1
    vector["K2LockedOriginal"] = k2
    vector["WhitenedTarget"] = y_white
    vector["K1Whitened"] = k1_white
    vector["K2LockedWhitened"] = k2_white
    vector["PolyDeg2Whitened"] = poly2_white
    vector["PolyDeg3Whitened"] = poly3_white
    vector["CovarianceStatus"] = "public_covariance_proxy_zero_sn_bao_cross_covariance"
    vector["SelectionUsesK2Score"] = False
    vector["LockedA2Changed"] = False
    vector["K1Refit"] = False
    vector["MeasurementValidationAllowed"] = False
    vector["ClaimBoundary"] = "whitened_standardized_branch_contrast_preflight_no_measurement_validation"
    OUT_VECTOR.parent.mkdir(parents=True, exist_ok=True)
    vector.to_csv(OUT_VECTOR, index=False)

    matrix = pd.DataFrame(whitening, columns=[str(idx) for idx in grid_indices])
    matrix.insert(0, "GridIndex", grid_indices)
    matrix.insert(0, "TargetConventionID", "WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1")
    matrix["CovarianceEigenvalue"] = eigvals
    matrix["CovariancePositiveDefinite"] = True
    matrix["ClaimBoundary"] = "whitening_matrix_preflight_no_measurement_validation"
    OUT_MATRIX.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(OUT_MATRIX, index=False)

    models = [
        ("K1_NO_MEMORY", k1, k1_white, 0, "fair_null"),
        ("K2_LOCKED_RHO4", k2, k2_white, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", zero, zero_white, 0, "diagnostic_control"),
        ("WEIGHTED_POLY_DEG2", poly2, poly2_white, 3, "overfit_risk_control"),
        ("WEIGHTED_POLY_DEG3", poly3, poly3_white, 4, "overfit_risk_control"),
    ]

    rows = []
    identity = np.eye(len(y_white))
    for model_id, pred_original, pred_white, parameter_count, model_class in models:
        full_chi2 = chi2(y, pred_original, cov)
        white_chi2 = chi2(y_white, pred_white, identity)
        rows.append(
            {
                "TargetConventionID": "WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1",
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": parameter_count,
                "FullCovarianceChi2": full_chi2,
                "WhitenedIdentityChi2": white_chi2,
                "Chi2ConsistencyAbsDiff": abs(full_chi2 - white_chi2),
                "AIC": aic(white_chi2, parameter_count),
                "BIC": bic(white_chi2, parameter_count, len(y)),
                "OriginalSignStableViolations": sign_violations(pred_original, y, stable),
                "WhitenedSignStableViolations": sign_violations(pred_white, y_white, stable),
                "MeanAbsWhitenedResidual": float(np.mean(np.abs(y_white - pred_white))),
                "SelectionUsesK2Score": False,
                "LockedA2Changed": False,
                "K1Refit": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "whitened_standardized_branch_contrast_preflight_no_measurement_validation",
            }
        )
    scorecard = pd.DataFrame(rows)
    k2_aic = float(scorecard.loc[scorecard["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
    scorecard["DeltaAIC_vs_K2"] = scorecard["AIC"] - k2_aic
    scorecard.to_csv(OUT_SCORECARD, index=False)

    k1_aic = float(scorecard.loc[scorecard["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
    best_poly_aic = float(scorecard[scorecard["ModelID"].str.contains("POLY")]["AIC"].min())
    best_model = scorecard.loc[scorecard["AIC"].idxmin()]
    k2_improves_k1 = k2_aic < k1_aic
    k2_beats_poly = k2_aic < best_poly_aic
    status = (
        "WHITENED_STANDARDIZED_BRANCH_CONTRAST_PREFLIGHT_SUPPORTIVE"
        if k2_improves_k1 and k2_beats_poly
        else "WHITENED_STANDARDIZED_BRANCH_CONTRAST_PREFLIGHT_MIXED_OR_WEAKENING"
    )
    summary = pd.DataFrame(
        [
            {
                "TargetConventionID": "WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1",
                "Rows": len(y),
                "CovariancePositiveDefinite": True,
                "CovarianceMinEigenvalue": float(np.min(eigvals)),
                "CovarianceMaxEigenvalue": float(np.max(eigvals)),
                "WhiteningUsesK2Score": False,
                "SelectionUsesK2Score": False,
                "LockedA2Changed": False,
                "LockedRho": 4.0,
                "LockedP": 3,
                "K1Refit": False,
                "BestModel": best_model["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_improves_k1,
                "K2BeatsBestPoly": k2_beats_poly,
                "MaxChi2ConsistencyAbsDiff": float(scorecard["Chi2ConsistencyAbsDiff"].max()),
                "SNBAOCrossCovarianceIncluded": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": status,
                "StrongestAllowedClaim": (
                    "a score-independent whitened standardized branch-contrast preflight target is now executable; "
                    "locked A2/K2 can be evaluated without changing the kernel or refitting K1"
                ),
                "PrimaryResidualRisk": (
                    "SN-BAO cross-covariance is still set to zero and polynomial controls remain strong, so this is not measurement validation"
                ),
                "NextAction": (
                    "replace the zero cross-covariance policy with a declared public joint covariance or registered shrinkage route, then rerun locked A2 unchanged"
                ),
                "ClaimBoundary": "whitened_standardized_branch_contrast_preflight_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Whitened Standardized Branch Contrast",
                "",
                "Status: executable preflight target convention; no measurement-validation claim.",
                "",
                "This target implements `WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1` by applying a declared public-covariance proxy whitening matrix to the standardized `SN - BAO` branch contrast.",
                "",
                "The construction is score-independent: it does not choose a target because of the K2 score, does not change the locked A2/K2 kernel, and does not refit K1.",
                "",
                "## Outputs",
                "",
                f"- Vector: `{OUT_VECTOR.relative_to(ROOT)}`",
                f"- Whitening matrix: `{OUT_MATRIX.relative_to(ROOT)}`",
                f"- Scorecard: `{OUT_SCORECARD.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "The route is still preflight-only because SN-BAO cross-covariance is not yet provided as a full public joint product. The result may strengthen or weaken A2/K2, but it cannot validate the measurement claim by itself.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_VECTOR}")
    print(f"Wrote {OUT_MATRIX}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
