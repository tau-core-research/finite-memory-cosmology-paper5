#!/usr/bin/env python3
"""Audit why weighted polynomial controls dominate in-sample.

The audit compares the two whitened covariance routes with small-sample
complexity penalties and simple out-of-sample diagnostics. It does not tune K2,
change rho, refit K1, or promote a measurement claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROUTES = [
    {
        "RouteID": "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        "Vector": EVIDENCE / "whitened_standardized_branch_contrast_vector.csv",
        "Scorecard": EVIDENCE / "whitened_standardized_branch_contrast_scorecard.csv",
        "TargetCol": "WhitenedTarget",
        "K1Col": "K1Whitened",
        "K2Col": "K2LockedWhitened",
        "Poly2Col": "PolyDeg2Whitened",
        "Poly3Col": "PolyDeg3Whitened",
    },
    {
        "RouteID": "REGISTERED_SHRINKAGE_WHITENED",
        "Vector": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_vector.csv",
        "Scorecard": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_scorecard.csv",
        "TargetCol": "WhitenedTarget",
        "K1Col": "K1Whitened",
        "K2Col": "K2LockedWhitened",
        "Poly2Col": "",
        "Poly3Col": "",
    },
]

OUT_ROW = EVIDENCE / "weighted_polynomial_dominance_row_audit.csv"
OUT_COMPLEXITY = EVIDENCE / "weighted_polynomial_complexity_audit.csv"
OUT_CV = EVIDENCE / "weighted_polynomial_out_of_sample_audit.csv"
OUT_SUMMARY = EVIDENCE / "weighted_polynomial_dominance_summary.csv"
OUT_DOC = DOCS / "weighted_polynomial_dominance_audit.md"


def aicc(aic: float, k: int, n: int) -> float:
    if n - k - 1 <= 0:
        return float("inf")
    return float(aic + (2 * k * (k + 1)) / (n - k - 1))


def fit_poly(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray, degree: int) -> np.ndarray:
    coeff = np.polyfit(x_train, y_train, degree)
    return np.polyval(coeff, x_eval)


def normalize_model_id(model_id: str) -> str:
    if "POLY_DEG2" in model_id:
        return "POLY_DEG2"
    if "POLY_DEG3" in model_id:
        return "POLY_DEG3"
    return model_id


def ensure_poly_columns(route: dict[str, object], vector: pd.DataFrame) -> pd.DataFrame:
    x = vector["x_coordinate"].to_numpy(float)
    y = vector[str(route["TargetCol"])].to_numpy(float)
    if not route["Poly2Col"]:
        vector["PolyDeg2Whitened"] = fit_poly(x, y, x, 2)
        route["Poly2Col"] = "PolyDeg2Whitened"
    if not route["Poly3Col"]:
        vector["PolyDeg3Whitened"] = fit_poly(x, y, x, 3)
        route["Poly3Col"] = "PolyDeg3Whitened"
    return vector


def row_audit(route: dict[str, object], vector: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    y = vector[str(route["TargetCol"])].to_numpy(float)
    models = [
        ("K1_NO_MEMORY", str(route["K1Col"]), 0),
        ("K2_LOCKED_RHO4", str(route["K2Col"]), 0),
        ("POLY_DEG2", str(route["Poly2Col"]), 3),
        ("POLY_DEG3", str(route["Poly3Col"]), 4),
    ]
    residuals = {}
    for model_id, col, _ in models:
        pred = vector[col].to_numpy(float)
        residuals[model_id] = y - pred

    k2_abs = np.abs(residuals["K2_LOCKED_RHO4"])
    poly2_abs = np.abs(residuals["POLY_DEG2"])
    poly3_abs = np.abs(residuals["POLY_DEG3"])
    for idx, row in vector.iterrows():
        for model_id, _, k in models:
            residual = float(residuals[model_id][idx])
            contribution = residual * residual
            rows.append(
                {
                    "AuditID": "WEIGHTED_POLYNOMIAL_DOMINANCE_ROW_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ComponentIndex": idx,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "ModelID": model_id,
                    "ParameterCount": k,
                    "WhitenedTarget": float(y[idx]),
                    "Prediction": float(y[idx] - residual),
                    "WhitenedResidual": residual,
                    "Chi2Component": contribution,
                    "K2AbsResidual": float(k2_abs[idx]),
                    "Poly2AbsResidual": float(poly2_abs[idx]),
                    "Poly3AbsResidual": float(poly3_abs[idx]),
                    "K2LosesToPoly2Here": bool(k2_abs[idx] > poly2_abs[idx]),
                    "K2LosesToPoly3Here": bool(k2_abs[idx] > poly3_abs[idx]),
                    "ClaimBoundary": "weighted_polynomial_row_audit_no_measurement_validation",
                }
            )
    return rows


def complexity_rows(route: dict[str, object], scorecard: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    n = int(scorecard["Rows"].iloc[0])
    for _, row in scorecard.iterrows():
        model_id = normalize_model_id(str(row["ModelID"]))
        k = int(row["ParameterCount"])
        aic_value = float(row["AIC"])
        rows.append(
            {
                "AuditID": "WEIGHTED_POLYNOMIAL_COMPLEXITY_AUDIT_V1",
                "RouteID": route["RouteID"],
                "ModelID": model_id,
                "Rows": n,
                "ParameterCount": k,
                "AIC": aic_value,
                "AICc": aicc(aic_value, k, n),
                "BIC": float(row["BIC"]),
                "SmallSamplePenaltyApplied": k > 0,
                "ClaimBoundary": "weighted_polynomial_complexity_audit_no_measurement_validation",
            }
        )
    return rows


def cv_rows(route: dict[str, object], vector: pd.DataFrame) -> list[dict[str, object]]:
    rows = []
    x = vector["x_coordinate"].to_numpy(float)
    y = vector[str(route["TargetCol"])].to_numpy(float)
    k1 = vector[str(route["K1Col"])].to_numpy(float)
    k2 = vector[str(route["K2Col"])].to_numpy(float)
    n = len(y)
    models_fixed = [("K1_NO_MEMORY", k1, 0), ("K2_LOCKED_RHO4", k2, 0)]

    for i in range(n):
        train = np.ones(n, dtype=bool)
        train[i] = False
        test = ~train
        fold_rows = []
        for model_id, pred, k in models_fixed:
            residual = y[test] - pred[test]
            fold_rows.append((model_id, k, float(np.mean(residual**2))))
        for degree in [2, 3]:
            pred = fit_poly(x[train], y[train], x[test], degree)
            residual = y[test] - pred
            fold_rows.append((f"POLY_DEG{degree}", degree + 1, float(np.mean(residual**2))))
        for model_id, k, mse in fold_rows:
            rows.append(
                {
                    "AuditID": "WEIGHTED_POLYNOMIAL_OUT_OF_SAMPLE_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ValidationMode": "leave_one_out",
                    "FoldID": f"component_{i}",
                    "ModelID": model_id,
                    "ParameterCount": k,
                    "TestN": 1,
                    "MeanSquaredWhitenedResidual": mse,
                    "ClaimBoundary": "weighted_polynomial_out_of_sample_audit_no_measurement_validation",
                }
            )

    blocks = {
        "low_depth": x <= 1 / 3,
        "mid_depth": (x > 1 / 3) & (x <= 2 / 3),
        "high_depth": x > 2 / 3,
    }
    for block_id, test in blocks.items():
        train = ~test
        if int(test.sum()) < 1 or int(train.sum()) < 4:
            continue
        for model_id, pred, k in models_fixed:
            residual = y[test] - pred[test]
            rows.append(
                {
                    "AuditID": "WEIGHTED_POLYNOMIAL_OUT_OF_SAMPLE_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ValidationMode": "blocked_depth",
                    "FoldID": block_id,
                    "ModelID": model_id,
                    "ParameterCount": k,
                    "TestN": int(test.sum()),
                    "MeanSquaredWhitenedResidual": float(np.mean(residual**2)),
                    "ClaimBoundary": "weighted_polynomial_out_of_sample_audit_no_measurement_validation",
                }
            )
        for degree in [2, 3]:
            pred = fit_poly(x[train], y[train], x[test], degree)
            residual = y[test] - pred
            rows.append(
                {
                    "AuditID": "WEIGHTED_POLYNOMIAL_OUT_OF_SAMPLE_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ValidationMode": "blocked_depth",
                    "FoldID": block_id,
                    "ModelID": f"POLY_DEG{degree}",
                    "ParameterCount": degree + 1,
                    "TestN": int(test.sum()),
                    "MeanSquaredWhitenedResidual": float(np.mean(residual**2)),
                    "ClaimBoundary": "weighted_polynomial_out_of_sample_audit_no_measurement_validation",
                }
            )
    return rows


def main() -> None:
    row_records: list[dict[str, object]] = []
    complexity_records: list[dict[str, object]] = []
    cv_records: list[dict[str, object]] = []

    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        vector = ensure_poly_columns(route, vector)
        scorecard = pd.read_csv(Path(str(route["Scorecard"])))
        scorecard["ModelID"] = scorecard["ModelID"].map(normalize_model_id)
        row_records.extend(row_audit(route, vector))
        complexity_records.extend(complexity_rows(route, scorecard))
        cv_records.extend(cv_rows(route, vector))

    row_df = pd.DataFrame(row_records)
    complexity_df = pd.DataFrame(complexity_records)
    cv_df = pd.DataFrame(cv_records)
    row_df.to_csv(OUT_ROW, index=False)
    complexity_df.to_csv(OUT_COMPLEXITY, index=False)
    cv_df.to_csv(OUT_CV, index=False)

    summary_rows = []
    for route_id in sorted(row_df["RouteID"].unique()):
        route_rows = row_df[row_df["RouteID"].eq(route_id)]
        route_complexity = complexity_df[complexity_df["RouteID"].eq(route_id)].copy()
        route_cv = cv_df[cv_df["RouteID"].eq(route_id)].copy()
        aic_best = route_complexity.loc[route_complexity["AIC"].idxmin()]
        aicc_best = route_complexity.loc[route_complexity["AICc"].idxmin()]
        bic_best = route_complexity.loc[route_complexity["BIC"].idxmin()]
        cv_summary = (
            route_cv.groupby(["ValidationMode", "ModelID"], as_index=False)["MeanSquaredWhitenedResidual"].mean()
        )
        loo = cv_summary[cv_summary["ValidationMode"].eq("leave_one_out")]
        blocked = cv_summary[cv_summary["ValidationMode"].eq("blocked_depth")]
        loo_best = loo.loc[loo["MeanSquaredWhitenedResidual"].idxmin()]
        blocked_best = (
            blocked.loc[blocked["MeanSquaredWhitenedResidual"].idxmin()]
            if not blocked.empty
            else pd.Series({"ModelID": "NO_BLOCKED_DEPTH_FOLD"})
        )
        k2_rows = route_rows[route_rows["ModelID"].eq("K2_LOCKED_RHO4")]
        summary_rows.append(
            {
                "AuditID": "WEIGHTED_POLYNOMIAL_DOMINANCE_SUMMARY_V1",
                "RouteID": route_id,
                "Rows": int(k2_rows["GridIndex"].nunique()),
                "K2LosesToPoly2Rows": int(k2_rows["K2LosesToPoly2Here"].sum()),
                "K2LosesToPoly3Rows": int(k2_rows["K2LosesToPoly3Here"].sum()),
                "BestAICModel": aic_best["ModelID"],
                "BestAICcModel": aicc_best["ModelID"],
                "BestBICModel": bic_best["ModelID"],
                "BestLeaveOneOutModel": loo_best["ModelID"],
                "BestBlockedDepthModel": blocked_best["ModelID"],
                "K2BeatsPolyUnderAICc": str(aicc_best["ModelID"]) == "K2_LOCKED_RHO4",
                "K2BeatsPolyUnderLeaveOneOut": str(loo_best["ModelID"]) == "K2_LOCKED_RHO4",
                "K2BeatsPolyUnderBlockedDepth": str(blocked_best["ModelID"]) == "K2_LOCKED_RHO4",
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "POLYNOMIAL_DOMINANCE_WEAKENS_UNDER_SMALL_SAMPLE_OR_OUT_OF_SAMPLE_AUDIT"
                    if str(aicc_best["ModelID"]) == "K2_LOCKED_RHO4"
                    or str(loo_best["ModelID"]) == "K2_LOCKED_RHO4"
                    or str(blocked_best["ModelID"]) == "K2_LOCKED_RHO4"
                    else "POLYNOMIAL_DOMINANCE_REMAINS_STABLE"
                ),
                "StrongestAllowedClaim": (
                    "weighted polynomial dominance is an in-sample control result and must be interpreted with small-sample and out-of-sample penalties"
                ),
                "ClaimBoundary": "weighted_polynomial_dominance_summary_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Weighted Polynomial Dominance Audit",
                "",
                "Status: diagnostic audit; no measurement-validation claim.",
                "",
                "This audit tests whether the weighted polynomial control remains stronger than locked K2 after row-level decomposition, small-sample AICc penalties, and simple out-of-sample checks.",
                "",
                "## Outputs",
                "",
                f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Complexity audit: `{OUT_COMPLEXITY.relative_to(ROOT)}`",
                f"- Out-of-sample audit: `{OUT_CV.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "The audit does not change A2/K2, does not choose a polynomial penalty after inspecting the K2 score, and does not authorize a measurement claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_COMPLEXITY}")
    print(f"Wrote {OUT_CV}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
