#!/usr/bin/env python3
"""Run physical-null proxy benchmarks on whitened covariance routes.

The physical-null templates are predeclared sanity/sensitivity controls. Their
amplitudes are not selected for interpretation and are not measurement-grade
calibrations.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

TEMPLATES = EVIDENCE / "physical_null_proxy_templates.csv"
AMPLITUDE_POLICY = EVIDENCE / "physical_null_amplitude_policy.csv"

ROUTES = [
    {
        "RouteID": "PUBLIC_PROXY_WHITENED_STANDARDIZED",
        "Vector": EVIDENCE / "whitened_standardized_branch_contrast_vector.csv",
        "Whitening": EVIDENCE / "whitened_standardized_branch_contrast_matrix.csv",
        "Covariance": None,
    },
    {
        "RouteID": "REGISTERED_SHRINKAGE_WHITENED",
        "Vector": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_vector.csv",
        "Whitening": None,
        "Covariance": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_covariance.csv",
    },
]

OUT_SCORECARD = EVIDENCE / "whitened_physical_null_benchmark_scorecard.csv"
OUT_ROW = EVIDENCE / "whitened_physical_null_benchmark_row_audit.csv"
OUT_SUMMARY = EVIDENCE / "whitened_physical_null_benchmark_summary.csv"
OUT_DOC = DOCS / "whitened_physical_null_benchmark.md"


def allowed_amplitudes(policy: pd.DataFrame) -> list[tuple[str, float, str]]:
    rows: list[tuple[str, float, str]] = []
    unit = policy[policy["PolicyID"].eq("PHYSNULL_AMP_UNIT_ONLY_V1")]
    if not unit.empty and unit["CanSupportScoringPreflight"].astype(str).str.lower().eq("true").all():
        rows.append(("PHYSNULL_AMP_UNIT_ONLY_V1", 1.0, "primary_sanity_preflight"))

    grid = policy[policy["PolicyID"].eq("PHYSNULL_AMP_BOUNDED_GRID_V1")]
    if not grid.empty and grid["CanSupportScoringPreflight"].astype(str).str.lower().eq("true").all():
        for amp in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            rows.append(("PHYSNULL_AMP_BOUNDED_GRID_V1", amp, "secondary_sensitivity_preflight_report_all"))
    return rows


def load_whitening(route: dict[str, object], grid_indices: list[int]) -> np.ndarray:
    if route["Whitening"] is not None:
        matrix_df = pd.read_csv(Path(str(route["Whitening"])))
        value_cols = [str(idx) for idx in grid_indices]
        return matrix_df[value_cols].to_numpy(float)

    cov_df = pd.read_csv(Path(str(route["Covariance"])))
    value_cols = [str(idx) for idx in grid_indices]
    cov = cov_df[value_cols].to_numpy(float)
    cov = 0.5 * (cov + cov.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    if np.any(eigvals <= 0.0):
        raise ValueError(f"non-positive covariance eigenvalue for {route['RouteID']}: {eigvals.min()}")
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def aic(chi2: float, k: int) -> float:
    return float(chi2) + 2 * int(k)


def bic(chi2: float, k: int, n: int) -> float:
    return float(chi2) + int(k) * float(np.log(n))


def score(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(residual @ residual)


def sign_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def main() -> None:
    templates = pd.read_csv(TEMPLATES)
    policy = pd.read_csv(AMPLITUDE_POLICY)
    amplitudes = allowed_amplitudes(policy)

    score_rows = []
    row_rows = []

    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        y_white = vector["WhitenedTarget"].to_numpy(float)
        k1_white = vector["K1Whitened"].to_numpy(float)
        k2_white = vector["K2LockedWhitened"].to_numpy(float)
        stable = vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()
        base_models = [
            ("K1_NO_MEMORY", "fair_null", k1_white, 0, "not_applicable", "not_applicable", False),
            ("K2_LOCKED_RHO4", "locked_prediction", k2_white, 0, "not_applicable", "not_applicable", False),
        ]

        route_templates = []
        for template_id, group in templates.groupby("TemplateID"):
            ordered = vector[["GridIndex"]].merge(
                group[["GridIndex", "NullID", "ProxyValue"]],
                on="GridIndex",
                how="left",
            )
            if ordered["ProxyValue"].isna().any():
                raise ValueError(f"Template {template_id} missing rows for {route['RouteID']}")
            shape_original = ordered["ProxyValue"].to_numpy(float)
            shape_white = whitening @ shape_original
            null_id = str(ordered["NullID"].iloc[0])
            for policy_id, amp, _policy_role in amplitudes:
                route_templates.append(
                    (
                        f"{null_id}_{template_id}_A{amp:+.1f}_{policy_id}",
                        "physical_null_preflight_sanity"
                        if policy_id == "PHYSNULL_AMP_UNIT_ONLY_V1"
                        else "physical_null_preflight_sensitivity",
                        amp * shape_white,
                        0,
                        policy_id,
                        amp,
                        False,
                    )
                )

        models = base_models + route_templates
        predictions: dict[str, np.ndarray] = {}
        for model_id, model_class, pred, k, policy_id, amp, amp_allowed in models:
            predictions[model_id] = pred
            c2 = score(y_white, pred)
            score_rows.append(
                {
                    "BenchmarkID": "WHITENED_PHYSICAL_NULL_BENCHMARK_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(y_white),
                    "ParameterCount": k,
                    "AmplitudePolicyID": policy_id,
                    "Amplitude": amp,
                    "AmplitudeSelectionAllowed": amp_allowed,
                    "WhitenedChi2": c2,
                    "AIC": aic(c2, k),
                    "BIC": bic(c2, k, len(y_white)),
                    "SignStableViolations": sign_violations(pred, y_white, stable),
                    "MeanAbsWhitenedResidual": float(np.mean(np.abs(y_white - pred))),
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "whitened_physical_null_benchmark_no_measurement_validation",
                }
            )

        physical_ids = [model_id for model_id, model_class, *_ in route_templates if model_class.startswith("physical_null")]
        phys_abs = np.vstack([np.abs(y_white - predictions[mid]) for mid in physical_ids])
        best_phys_idx = np.argmin(phys_abs, axis=0)
        k2_abs = np.abs(y_white - k2_white)
        for i, row in vector.iterrows():
            best_model = physical_ids[int(best_phys_idx[i])]
            best_pred = predictions[best_model][i]
            row_rows.append(
                {
                    "BenchmarkID": "WHITENED_PHYSICAL_NULL_BENCHMARK_ROW_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ComponentIndex": i,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "WhitenedTarget": float(y_white[i]),
                    "K2Prediction": float(k2_white[i]),
                    "K2Residual": float(y_white[i] - k2_white[i]),
                    "K2Chi2Component": float((y_white[i] - k2_white[i]) ** 2),
                    "BestPhysicalModelID": best_model,
                    "BestPhysicalPrediction": float(best_pred),
                    "BestPhysicalResidual": float(y_white[i] - best_pred),
                    "BestPhysicalChi2Component": float((y_white[i] - best_pred) ** 2),
                    "K2StrongerThanBestPhysicalHere": bool(k2_abs[i] < abs(y_white[i] - best_pred)),
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "whitened_physical_null_benchmark_row_no_measurement_validation",
                }
            )

    scorecard = pd.DataFrame(score_rows)
    row_audit = pd.DataFrame(row_rows)
    scorecard.to_csv(OUT_SCORECARD, index=False)
    row_audit.to_csv(OUT_ROW, index=False)

    summary_rows = []
    for route_id, group in scorecard.groupby("RouteID", sort=True):
        physical = group[group["ModelClass"].astype(str).str.startswith("physical_null")]
        best_physical = physical.loc[physical["AIC"].idxmin()]
        k1 = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        k2 = group[group["ModelID"].eq("K2_LOCKED_RHO4")].iloc[0]
        rows_route = row_audit[row_audit["RouteID"].eq(route_id)]
        summary_rows.append(
            {
                "BenchmarkID": "WHITENED_PHYSICAL_NULL_BENCHMARK_V1",
                "RouteID": route_id,
                "Rows": int(k2["Rows"]),
                "PhysicalNullRows": len(physical),
                "BestPhysicalNullModelForDiagnosticsOnly": best_physical["ModelID"],
                "BestPhysicalNullAIC": float(best_physical["AIC"]),
                "K1AIC": float(k1["AIC"]),
                "K2AIC": float(k2["AIC"]),
                "DeltaAIC_K2_minus_K1": float(k2["AIC"] - k1["AIC"]),
                "DeltaAIC_K2_minus_BestPhysicalNull": float(k2["AIC"] - best_physical["AIC"]),
                "K2ImprovesOverK1": float(k2["AIC"]) < float(k1["AIC"]),
                "K2BeatsBestPhysicalNull": float(k2["AIC"]) < float(best_physical["AIC"]),
                "RowsWhereK2StrongerThanBestPhysical": int(rows_route["K2StrongerThanBestPhysicalHere"].sum()),
                "AnyAmplitudeSelectedForInterpretation": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "WHITENED_PHYSICAL_NULL_PREFLIGHT_SUPPORTS_K2"
                    if float(k2["AIC"]) < float(best_physical["AIC"])
                    else "WHITENED_PHYSICAL_NULL_PREFLIGHT_MIXED_OR_WEAKENING"
                ),
                "StrongestAllowedClaim": (
                    "locked K2 is stronger than the current predeclared physical-null proxy layer on the whitened route"
                    if float(k2["AIC"]) < float(best_physical["AIC"])
                    else "physical-null proxy layer remains competitive on the whitened route"
                ),
                "PrimaryResidualRisk": (
                    "physical null amplitudes remain proxy/sensitivity values, not externally calibrated measurement-grade controls"
                ),
                "ClaimBoundary": "whitened_physical_null_benchmark_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Whitened Physical Null Benchmark",
                "",
                "Status: physical-null proxy benchmark on whitened covariance routes; no measurement-validation claim.",
                "",
                "This benchmark applies the predeclared backreaction and Dyer-Roeder physical-null proxy templates to the same whitened branch-contrast routes used for K2. Amplitudes are reported from the predeclared policy and are not selected for interpretation.",
                "",
                "## Outputs",
                "",
                f"- Scorecard: `{OUT_SCORECARD.relative_to(ROOT)}`",
                f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
                "",
                "## Boundary",
                "",
                "The result can compare K2 against current physical-null proxy controls, but cannot validate a measurement claim until the physical-null amplitudes and covariance are externally calibrated.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
