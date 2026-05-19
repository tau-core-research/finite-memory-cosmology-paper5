#!/usr/bin/env python3
"""Row-level diagnosis of A2 vs polynomial controls.

The script keeps K2/A2 fixed. It only decomposes where polynomial controls win
or lose under the existing preflight routes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PUBLIC_MARGINALS = EVIDENCE / "source_split_likelihood_native_public_covariance_proxy_marginals.csv"
BRANCH_SCATTER = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_polynomial_row_tension_audit.csv"
SUMMARY = EVIDENCE / "k2_a2_polynomial_row_tension_summary.csv"


def weighted_poly_predict(x_train, y_train, sigma_train, x_test, degree: int) -> np.ndarray:
    weights = np.where(sigma_train > 0.0, 1.0 / sigma_train, 0.0)
    coeff = np.polyfit(x_train, y_train, degree, w=weights)
    return np.polyval(coeff, x_test)


def depth_zone(x: float) -> str:
    if x <= 0.5:
        return "low_depth"
    if x <= 0.8:
        return "mid_depth"
    return "high_depth"


def load_data() -> pd.DataFrame:
    target = pd.read_csv(TARGET)
    pred = pd.read_csv(PRED)
    public = pd.read_csv(PUBLIC_MARGINALS)[["GridIndex", "SigmaPublicProxy"]]
    branch = pd.read_csv(BRANCH_SCATTER)[["GridIndex", "BranchScatterSigma", "SigmaCombinedQuadrature"]]
    return (
        target[target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])]
        [["GridIndex", "z_grid", "x_coordinate", "SourceSplitResponse", "SignStableTemplate", "SNBAOSameSign"]]
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
        .merge(public, on="GridIndex", how="inner")
        .merge(branch, on="GridIndex", how="inner")
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )


def loo_rows(data: pd.DataFrame, sigma_route: str, degree: int) -> list[dict[str, object]]:
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    a2 = data["K2SourceSplitA2Prediction"].to_numpy(float)
    sigma = data[sigma_route].to_numpy(float)
    rows: list[dict[str, object]] = []
    for idx in range(len(data)):
        test = np.zeros(len(data), dtype=bool)
        test[idx] = True
        train = ~test
        poly = weighted_poly_predict(x[train], y[train], sigma[train], x[test], degree)[0]
        a2_residual = y[idx] - a2[idx]
        poly_residual = y[idx] - poly
        a2_chi2 = float((a2_residual / sigma[idx]) ** 2)
        poly_chi2 = float((poly_residual / sigma[idx]) ** 2)
        rows.append(
            {
                "ValidationMode": "leave_one_out",
                "SigmaRoute": sigma_route,
                "PolynomialModel": f"POLY_DEG{degree}",
                "GridIndex": int(data.loc[idx, "GridIndex"]),
                "z": float(data.loc[idx, "z_grid"]),
                "x": float(x[idx]),
                "DepthZone": depth_zone(float(x[idx])),
                "Target": float(y[idx]),
                "A2Prediction": float(a2[idx]),
                "PolynomialPrediction": float(poly),
                "Sigma": float(sigma[idx]),
                "A2Residual": float(a2_residual),
                "PolynomialResidual": float(poly_residual),
                "A2Chi2": a2_chi2,
                "PolynomialChi2": poly_chi2,
                "DeltaChi2_A2_minus_Poly": a2_chi2 - poly_chi2,
                "A2BeatsPolynomial": a2_chi2 < poly_chi2,
                "SignStable": bool(str(data.loc[idx, "SignStableTemplate"]).lower() in {"true", "1", "yes"}),
                "SNBAOSameSign": bool(str(data.loc[idx, "SNBAOSameSign"]).lower() in {"true", "1", "yes"}),
                "ClaimBoundary": "row_tension_no_measurement_validation",
            }
        )
    return rows


def blocked_rows(data: pd.DataFrame, sigma_route: str, degree: int) -> list[dict[str, object]]:
    x = data["x_coordinate"].to_numpy(float)
    y = data["SourceSplitResponse"].to_numpy(float)
    a2 = data["K2SourceSplitA2Prediction"].to_numpy(float)
    sigma = data[sigma_route].to_numpy(float)
    zones = np.array([depth_zone(v) for v in x])
    rows: list[dict[str, object]] = []
    for zone in ["low_depth", "mid_depth", "high_depth"]:
        test = zones == zone
        train = ~test
        if int(test.sum()) < 1 or int(train.sum()) < 5:
            continue
        poly_values = weighted_poly_predict(x[train], y[train], sigma[train], x[test], degree)
        for row_i, poly in zip(np.where(test)[0], poly_values):
            a2_residual = y[row_i] - a2[row_i]
            poly_residual = y[row_i] - poly
            a2_chi2 = float((a2_residual / sigma[row_i]) ** 2)
            poly_chi2 = float((poly_residual / sigma[row_i]) ** 2)
            rows.append(
                {
                    "ValidationMode": f"blocked_{zone}",
                    "SigmaRoute": sigma_route,
                    "PolynomialModel": f"POLY_DEG{degree}",
                    "GridIndex": int(data.loc[row_i, "GridIndex"]),
                    "z": float(data.loc[row_i, "z_grid"]),
                    "x": float(x[row_i]),
                    "DepthZone": zone,
                    "Target": float(y[row_i]),
                    "A2Prediction": float(a2[row_i]),
                    "PolynomialPrediction": float(poly),
                    "Sigma": float(sigma[row_i]),
                    "A2Residual": float(a2_residual),
                    "PolynomialResidual": float(poly_residual),
                    "A2Chi2": a2_chi2,
                    "PolynomialChi2": poly_chi2,
                    "DeltaChi2_A2_minus_Poly": a2_chi2 - poly_chi2,
                    "A2BeatsPolynomial": a2_chi2 < poly_chi2,
                    "SignStable": bool(str(data.loc[row_i, "SignStableTemplate"]).lower() in {"true", "1", "yes"}),
                    "SNBAOSameSign": bool(str(data.loc[row_i, "SNBAOSameSign"]).lower() in {"true", "1", "yes"}),
                    "ClaimBoundary": "row_tension_no_measurement_validation",
                }
            )
    return rows


def main() -> None:
    data = load_data()
    sigma_routes = {
        "public_proxy_diag": "SigmaPublicProxy",
        "branch_scatter_diag": "BranchScatterSigma",
        "native_plus_branch_scatter_quadrature": "SigmaCombinedQuadrature",
    }
    rows: list[dict[str, object]] = []
    for route_id, sigma_col in sigma_routes.items():
        for degree in [2, 3]:
            for item in loo_rows(data, sigma_col, degree):
                item["SigmaRoute"] = route_id
                rows.append(item)
            for item in blocked_rows(data, sigma_col, degree):
                item["SigmaRoute"] = route_id
                rows.append(item)
    detail = pd.DataFrame(rows)
    detail.to_csv(OUT, index=False)

    summary_rows = []
    for (route, mode, poly), group in detail.groupby(["SigmaRoute", "ValidationMode", "PolynomialModel"], sort=False):
        summary_rows.append(
            {
                "SigmaRoute": route,
                "ValidationMode": mode,
                "PolynomialModel": poly,
                "Rows": len(group),
                "A2Wins": int(group["A2BeatsPolynomial"].astype(bool).sum()),
                "PolyWins": int((~group["A2BeatsPolynomial"].astype(bool)).sum()),
                "A2TotalChi2": float(group["A2Chi2"].sum()),
                "PolynomialTotalChi2": float(group["PolynomialChi2"].sum()),
                "DeltaChi2_A2_minus_Poly": float(group["DeltaChi2_A2_minus_Poly"].sum()),
                "SignStableRows": int(group["SignStable"].astype(bool).sum()),
                "A2WinsSignStable": int(group[group["SignStable"].astype(bool)]["A2BeatsPolynomial"].astype(bool).sum()),
                "ClaimBoundary": "row_tension_no_measurement_validation",
            }
        )
    pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
