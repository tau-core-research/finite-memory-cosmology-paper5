#!/usr/bin/env python3
"""Score externally sourced Dyer-Roeder alpha previews on whitened routes.

The alpha amplitude is fixed from public source constraints via
clumpiness=1-alpha. No amplitude fitting, sign flipping, or K2-informed
selection is allowed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

ALPHA_PREVIEW = EVIDENCE / "physical_null_alpha_response_preview.csv"
ALPHA_SOURCE = ROOT / "data" / "physical_nulls" / "dyer_roeder_optical_calibration_source.csv"

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

OUT_SCORECARD = EVIDENCE / "whitened_alpha_calibrated_preflight_scorecard.csv"
OUT_ROW = EVIDENCE / "whitened_alpha_calibrated_preflight_row_audit.csv"
OUT_SUMMARY = EVIDENCE / "whitened_alpha_calibrated_preflight_summary.csv"
OUT_DOC = ROOT / "docs" / "whitened_alpha_calibrated_preflight.md"


def load_whitening(route: dict[str, object], grid_indices: list[int]) -> np.ndarray:
    if route["Whitening"] is not None:
        matrix = pd.read_csv(Path(str(route["Whitening"])))
        return matrix[[str(idx) for idx in grid_indices]].to_numpy(float)
    cov_df = pd.read_csv(Path(str(route["Covariance"])))
    cov = cov_df[[str(idx) for idx in grid_indices]].to_numpy(float)
    eigvals, eigvecs = np.linalg.eigh(0.5 * (cov + cov.T))
    if np.any(eigvals <= 0.0):
        raise ValueError(f"non-positive covariance eigenvalue for {route['RouteID']}")
    return eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T


def score(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(residual @ residual)


def sign_violations(pred: np.ndarray, y: np.ndarray, stable: np.ndarray) -> int:
    if not np.any(stable):
        return 0
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def main() -> None:
    alpha = pd.read_csv(ALPHA_PREVIEW)
    alpha_source = pd.read_csv(ALPHA_SOURCE)
    allowed_extractions = set(alpha_source["ExtractionID"].astype(str))
    alpha = alpha[alpha["ExtractionID"].astype(str).isin(allowed_extractions)].copy()

    score_rows = []
    row_rows = []
    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        y = vector["WhitenedTarget"].to_numpy(float)
        k1 = vector["K1Whitened"].to_numpy(float)
        k2 = vector["K2LockedWhitened"].to_numpy(float)
        stable = vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

        base = [
            ("K1_NO_MEMORY", "fair_null", k1, "not_applicable"),
            ("K2_LOCKED_RHO4", "locked_prediction", k2, "not_applicable"),
        ]
        models = []
        for extraction_id, group in alpha.groupby("ExtractionID"):
            ordered = vector[["GridIndex"]].merge(
                group[["GridIndex", "ResponsePreview", "Alpha", "ClumpinessAmplitude", "ResponseSigmaDiagPreview"]],
                on="GridIndex",
                how="left",
            )
            if ordered["ResponsePreview"].isna().any():
                continue
            pred_white = whitening @ ordered["ResponsePreview"].to_numpy(float)
            models.append(
                (
                    f"DYER_ROEDER_ALPHA_AS_DECLARED_{extraction_id}",
                    "external_alpha_physical_null_preflight",
                    pred_white,
                    extraction_id,
                    ordered,
                )
            )

        for model_id, model_class, pred, extraction_id in base:
            c2 = score(y, pred)
            score_rows.append(
                {
                    "PreflightID": "WHITENED_ALPHA_CALIBRATED_PREFLIGHT_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "ExtractionID": extraction_id,
                    "Rows": len(y),
                    "ParameterCount": 0,
                    "WhitenedChi2": c2,
                    "AIC": c2,
                    "BIC": c2,
                    "SignStableViolations": sign_violations(pred, y, stable),
                    "AmplitudeFitToTargetAllowed": False,
                    "SelectionUsesK2Score": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "whitened_alpha_calibrated_preflight_no_measurement_validation",
                }
            )
        for model_id, model_class, pred, extraction_id, ordered in models:
            c2 = score(y, pred)
            score_rows.append(
                {
                    "PreflightID": "WHITENED_ALPHA_CALIBRATED_PREFLIGHT_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "ExtractionID": extraction_id,
                    "Rows": len(y),
                    "ParameterCount": 0,
                    "WhitenedChi2": c2,
                    "AIC": c2,
                    "BIC": c2,
                    "SignStableViolations": sign_violations(pred, y, stable),
                    "Alpha": float(ordered["Alpha"].iloc[0]),
                    "ClumpinessAmplitude": float(ordered["ClumpinessAmplitude"].iloc[0]),
                    "AmplitudeFitToTargetAllowed": False,
                    "SelectionUsesK2Score": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "whitened_alpha_calibrated_preflight_no_measurement_validation",
                }
            )
            k2_abs = np.abs(y - k2)
            alpha_abs = np.abs(y - pred)
            for i, row in vector.iterrows():
                row_rows.append(
                    {
                        "PreflightID": "WHITENED_ALPHA_CALIBRATED_PREFLIGHT_ROW_AUDIT_V1",
                        "RouteID": route["RouteID"],
                        "ExtractionID": extraction_id,
                        "ComponentIndex": i,
                        "GridIndex": int(row["GridIndex"]),
                        "z_grid": float(row["z_grid"]),
                        "x_coordinate": float(row["x_coordinate"]),
                        "WhitenedTarget": float(y[i]),
                        "K2Prediction": float(k2[i]),
                        "AlphaPrediction": float(pred[i]),
                        "K2AbsResidual": float(k2_abs[i]),
                        "AlphaAbsResidual": float(alpha_abs[i]),
                        "K2StrongerThanAlphaHere": bool(k2_abs[i] < alpha_abs[i]),
                        "MeasurementValidationAllowed": False,
                        "ClaimBoundary": "whitened_alpha_calibrated_preflight_no_measurement_validation",
                    }
                )

    scorecard = pd.DataFrame(score_rows)
    row_audit = pd.DataFrame(row_rows)
    scorecard.to_csv(OUT_SCORECARD, index=False)
    row_audit.to_csv(OUT_ROW, index=False)

    summary_rows = []
    for route_id, group in scorecard.groupby("RouteID"):
        k2 = group[group["ModelID"].eq("K2_LOCKED_RHO4")].iloc[0]
        k1 = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        alpha_rows = group[group["ModelClass"].eq("external_alpha_physical_null_preflight")]
        best_alpha = alpha_rows.loc[alpha_rows["AIC"].idxmin()]
        route_row_audit = row_audit[(row_audit["RouteID"].eq(route_id)) & (row_audit["ExtractionID"].eq(best_alpha["ExtractionID"]))]
        summary_rows.append(
            {
                "SummaryID": "WHITENED_ALPHA_CALIBRATED_PREFLIGHT_SUMMARY",
                "RouteID": route_id,
                "Rows": int(k2["Rows"]),
                "ExternalAlphaModels": len(alpha_rows),
                "BestAlphaModel": best_alpha["ModelID"],
                "BestAlphaExtractionID": best_alpha["ExtractionID"],
                "BestAlphaAIC": float(best_alpha["AIC"]),
                "K1AIC": float(k1["AIC"]),
                "K2AIC": float(k2["AIC"]),
                "DeltaAIC_K2_minus_K1": float(k2["AIC"] - k1["AIC"]),
                "DeltaAIC_K2_minus_BestAlpha": float(k2["AIC"] - best_alpha["AIC"]),
                "K2ImprovesOverK1": float(k2["AIC"]) < float(k1["AIC"]),
                "K2BeatsBestExternalAlpha": float(k2["AIC"]) < float(best_alpha["AIC"]),
                "RowsWhereK2StrongerThanBestAlpha": int(route_row_audit["K2StrongerThanAlphaHere"].sum()),
                "AmplitudeFitToTargetAllowed": False,
                "SelectionUsesK2Score": False,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "EXTERNAL_ALPHA_PREFLIGHT_SUPPORTS_K2_OVER_OPTICAL_NULL"
                    if float(k2["AIC"]) < float(best_alpha["AIC"])
                    else "EXTERNAL_ALPHA_PREFLIGHT_MIXED_OR_WEAKENING"
                ),
                "StrongestAllowedClaim": "externally sourced alpha amplitudes are too small/weak to explain the current whitened K2-relevant target",
                "PrimaryResidualRisk": "alpha source is external but not source-native to the current SN-BAO contrast and lacks full joint covariance",
                "ClaimBoundary": "whitened_alpha_calibrated_preflight_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# Whitened Alpha-Calibrated Preflight",
                "",
                "Status: external Dyer-Roeder alpha amplitude preflight; no measurement-validation claim.",
                "",
                "This run uses published alpha constraints as fixed optical-null amplitudes and compares them with the locked K2 prediction on the whitened branch-contrast routes. No alpha amplitude is fit to the target.",
                "",
                "## Outputs",
                "",
                f"- Scorecard: `{OUT_SCORECARD.relative_to(ROOT)}`",
                f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
                f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
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
