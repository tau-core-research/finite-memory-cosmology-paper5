#!/usr/bin/env python3
"""Run locked A2 over registered joint-covariance routes.

This script does not select a best route for stronger interpretation. It writes
the route-by-route scorecard needed to decide whether FG_4 can advance beyond
preflight.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.joint_covariance import positive_definite_status, registered_shrinkage, row_aligned_cross_source_split
from fmc.likelihood import aic, bic, chi2
from fmc.operators import w_k2_locked

EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

PUBLIC_COV = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy.csv"
PUBLIC_PROXY_SUMMARY = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_summary.csv"
BRANCH_COV = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"
REGISTERED_SHRINKAGE = EVIDENCE / "registered_shrinkage_parameter_policy_readiness.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
EXTERNAL_K1 = DATA / "k1" / "source_split_external_k1_response.csv"

OUT_ROUTES = EVIDENCE / "joint_covariance_route_registry.csv"
OUT_SCORECARD = EVIDENCE / "joint_covariance_route_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "joint_covariance_route_summary.csv"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_matrix_rows(path: Path) -> tuple[list[int], np.ndarray]:
    df = pd.read_csv(path)
    indices = df["GridIndex"].astype(int).to_list()
    value_cols = [col for col in df.columns if col not in {"CovarianceID", "GridIndex", "CovarianceStatus", "ClaimBoundary"}]
    return indices, df[value_cols].to_numpy(float)


def branch_scatter_covariance() -> tuple[list[int], np.ndarray]:
    rows = pd.read_csv(BRANCH_COV).sort_values("GridIndex")
    indices = rows["GridIndex"].astype(int).to_list()
    sigma = rows["BranchScatterSigma"].to_numpy(float)
    return indices, np.diag(sigma * sigma)


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


def route_definitions(public_cov: np.ndarray, branch_cov: np.ndarray, x: np.ndarray) -> list[dict[str, object]]:
    shrinkage = pd.read_csv(REGISTERED_SHRINKAGE).iloc[0]
    lam = float(shrinkage["PrimaryLambdaShrink"])
    corr_len = float(shrinkage["PrimaryCorrelationLength"])
    routes = [
        {
            "RouteID": "JCOV_PUBLIC_ZERO_CROSS_V1",
            "RouteClass": "public_proxy_preflight",
            "Covariance": public_cov,
            "Predeclared": True,
            "CanSupportMeasurementValidation": False,
            "PrimaryLimitation": "zero SN-BAO cross-covariance and binned/anchored transform",
        },
        {
            "RouteID": "JCOV_PUBLIC_REGISTERED_SHRINKAGE_V1",
            "RouteClass": "registered_public_proxy_preflight",
            "Covariance": registered_shrinkage(public_cov, lambda_shrink=lam, x=x, correlation_length=corr_len),
            "Predeclared": truthy(shrinkage["ParameterPolicyRegistered"]) and truthy(shrinkage["CrossCovariancePolicyRegistered"]),
            "CanSupportMeasurementValidation": False,
            "PrimaryLimitation": "registered sensitivity route; not public full covariance",
        },
        {
            "RouteID": "JCOV_PUBLIC_ROW_CROSS_RHO0_V1",
            "RouteClass": "cross_covariance_sensitivity_only",
            "Covariance": row_aligned_cross_source_split(public_cov / 2.0, public_cov / 2.0, rho_cross=0.0),
            "Predeclared": True,
            "CanSupportMeasurementValidation": False,
            "PrimaryLimitation": "diagnostic decomposition only; not likelihood-native cross-covariance",
        },
        {
            "RouteID": "JCOV_BRANCH_SCATTER_BRIDGE_V1",
            "RouteClass": "calibrated_preflight_bridge",
            "Covariance": branch_cov,
            "Predeclared": True,
            "CanSupportMeasurementValidation": False,
            "PrimaryLimitation": "independently calibrated preflight bridge; not full public covariance",
        },
    ]
    return routes


def main() -> None:
    public_indices, public_cov = load_matrix_rows(PUBLIC_COV)
    branch_indices, branch_cov = branch_scatter_covariance()
    if public_indices != branch_indices:
        raise ValueError("public covariance and branch covariance grid indices differ")

    target = pd.read_csv(TARGET)
    external = pd.read_csv(EXTERNAL_K1)
    data = (
        external.merge(
            target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
            on="GridIndex",
            how="inner",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )
    data = data[data["GridIndex"].isin(public_indices)].copy()
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    stable = data["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

    route_rows = []
    score_rows = []
    for route in route_definitions(public_cov, branch_cov, x):
        route_id = str(route["RouteID"])
        cov = np.asarray(route["Covariance"], dtype=float) + np.eye(len(public_indices)) * 1e-12
        pd_ok, eig_min, eig_max = positive_definite_status(cov)
        route_rows.append(
            {
                "RouteID": route_id,
                "RouteClass": route["RouteClass"],
                "Rows": len(public_indices),
                "PositiveDefinite": pd_ok,
                "MinEigenvalue": eig_min,
                "MaxEigenvalue": eig_max,
                "Predeclared": route["Predeclared"],
                "CanSupportMeasurementValidation": route["CanSupportMeasurementValidation"],
                "PrimaryLimitation": route["PrimaryLimitation"],
                "ClaimBoundary": "joint_covariance_route_no_measurement_validation",
            }
        )
        if not pd_ok:
            continue
        for model_id, pred, k, model_class in model_rows(x, y, k1):
            c2 = chi2(y, pred, cov)
            score_rows.append(
                {
                    "RouteID": route_id,
                    "RouteClass": route["RouteClass"],
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(y),
                    "ParameterCount": k,
                    "Chi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y)),
                    "SignStableViolations": int(np.sum(np.sign(pred[stable]) != np.sign(y[stable]))),
                    "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                    "ClaimBoundary": "joint_covariance_route_no_measurement_validation",
                }
            )

    registry = pd.DataFrame(route_rows)
    scorecard = pd.DataFrame(score_rows)
    registry.to_csv(OUT_ROUTES, index=False)
    scorecard.to_csv(OUT_SCORECARD, index=False)

    summary_rows = []
    for route_id, group in scorecard.groupby("RouteID", sort=False):
        best = group.loc[group["AIC"].idxmin()]
        k1_aic = float(group.loc[group["ModelID"].eq("K1_NO_MEMORY"), "AIC"].iloc[0])
        k2_aic = float(group.loc[group["ModelID"].eq("K2_LOCKED_RHO4"), "AIC"].iloc[0])
        best_poly_aic = float(group[group["ModelID"].str.startswith("POLY")]["AIC"].min())
        route_meta = registry[registry["RouteID"].eq(route_id)].iloc[0]
        summary_rows.append(
            {
                "RouteID": route_id,
                "RouteClass": route_meta["RouteClass"],
                "BestModel": best["ModelID"],
                "K1AIC": k1_aic,
                "K2AIC": k2_aic,
                "BestPolyAIC": best_poly_aic,
                "DeltaAIC_K2_minus_K1": k2_aic - k1_aic,
                "DeltaAIC_K2_minus_BestPoly": k2_aic - best_poly_aic,
                "K2ImprovesOverK1": k2_aic < k1_aic,
                "K2BeatsBestPoly": k2_aic < best_poly_aic,
                "CanSupportMeasurementValidation": False,
                "Interpretation": (
                    "k2_supportive_against_k1_and_polynomial_under_this_preflight_route"
                    if k2_aic < k1_aic and k2_aic < best_poly_aic
                    else "k2_supportive_against_k1_but_polynomial_or_control_remains_competitive"
                    if k2_aic < k1_aic
                    else "k2_not_supportive_under_this_route"
                ),
                "ClaimBoundary": "joint_covariance_route_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_ROUTES}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
