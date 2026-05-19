#!/usr/bin/env python3
"""Compare provisional BAO-only backreaction curve against K2 routes.

This is a bridge audit, not a measurement-level physical-null score. The
backreaction observable Omega_R + 3 Omega_Q is not the same observable as the
whitened branch-contrast vector. We therefore report raw/interpolated shape,
sign, and required scaling diagnostics while keeping any fitted bridge scale out
of the allowed claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
DATA = ROOT / "data" / "physical_nulls" / "backreaction_reproduction"

OMEGA = DATA / "provisional_bao_backreaction_omega_curve.csv"

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

OUT_ROW = EVIDENCE / "provisional_backreaction_preflight_row_audit.csv"
OUT_SCORECARD = EVIDENCE / "provisional_backreaction_preflight_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "provisional_backreaction_preflight_summary.csv"
OUT_DOC = DOCS / "provisional_backreaction_preflight_comparison.md"


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


def chi2(y: np.ndarray, pred: np.ndarray) -> float:
    residual = y - pred
    return float(residual @ residual)


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) == 0.0 or np.std(b) == 0.0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def best_scalar_to_match(y: np.ndarray, shape: np.ndarray) -> float:
    denom = float(shape @ shape)
    if denom <= 0.0:
        return float("nan")
    return float((shape @ y) / denom)


def normalized_shape(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    centered = arr - float(np.mean(arr))
    norm = float(np.linalg.norm(centered))
    if norm <= 0.0:
        return centered
    return centered / norm


def sign_matches(a: np.ndarray, b: np.ndarray, stable: np.ndarray | None = None) -> int:
    if stable is None:
        mask = np.ones(len(a), dtype=bool)
    else:
        mask = np.asarray(stable, dtype=bool)
    return int(np.sum(np.sign(a[mask]) == np.sign(b[mask])))


def main() -> None:
    omega = pd.read_csv(OMEGA)
    omega_z = omega["z"].to_numpy(float)
    omega_val = omega["Omega_R_plus_3Omega_Q"].to_numpy(float)
    omega_sig = omega["OmegaSigma"].to_numpy(float)

    row_rows = []
    score_rows = []
    summary_rows = []

    for route in ROUTES:
        vector = pd.read_csv(Path(str(route["Vector"])))
        grid_indices = vector["GridIndex"].astype(int).to_list()
        whitening = load_whitening(route, grid_indices)
        z = vector["z_grid"].to_numpy(float)
        target = vector["WhitenedTarget"].to_numpy(float)
        k1 = vector["K1Whitened"].to_numpy(float)
        k2 = vector["K2LockedWhitened"].to_numpy(float)
        stable = vector["SignStableTemplate"].astype(str).str.lower().eq("true").to_numpy()

        omega_interp = np.interp(z, omega_z, omega_val)
        omega_sigma_interp = np.interp(z, omega_z, omega_sig)
        omega_white_raw = whitening @ omega_interp
        omega_shape_white = whitening @ normalized_shape(omega_interp)

        models = [
            (
                "BACKREACTION_RAW_INTERPOLATED",
                omega_white_raw,
                "raw_interpolated_bridge_sensitivity_not_same_observable",
                False,
                False,
            ),
            (
                "BACKREACTION_UNIT_SHAPE",
                omega_shape_white,
                "shape_only_bridge_sensitivity_not_physical_amplitude",
                False,
                False,
            ),
        ]
        for model_id, pred, model_class, scale_fit_allowed, measurement_allowed in models:
            score_rows.append(
                {
                    "AuditID": "PROVISIONAL_BACKREACTION_PREFLIGHT_COMPARISON_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": model_id,
                    "ModelClass": model_class,
                    "Rows": len(target),
                    "Chi2AgainstTarget": chi2(target, pred),
                    "Chi2AgainstK2": chi2(k2, pred),
                    "CorrelationWithTarget": corr(target, pred),
                    "CorrelationWithK2": corr(k2, pred),
                    "SignMatchesTargetAll": sign_matches(pred, target),
                    "SignMatchesTargetStable": sign_matches(pred, target, stable),
                    "StableRows": int(np.sum(stable)),
                    "ScaleFitAllowed": scale_fit_allowed,
                    "MeasurementValidationAllowed": measurement_allowed,
                    "ClaimBoundary": "provisional_backreaction_preflight_no_measurement_validation",
                }
            )

        alpha_to_target = best_scalar_to_match(target, omega_white_raw)
        alpha_to_k2 = best_scalar_to_match(k2, omega_white_raw)
        scaled_to_target = alpha_to_target * omega_white_raw
        scaled_to_k2 = alpha_to_k2 * omega_white_raw
        score_rows.extend(
            [
                {
                    "AuditID": "PROVISIONAL_BACKREACTION_PREFLIGHT_COMPARISON_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": "BACKREACTION_FORBIDDEN_BEST_SCALE_TO_TARGET",
                    "ModelClass": "forbidden_same_scorecard_scale_diagnostic_only",
                    "Rows": len(target),
                    "Chi2AgainstTarget": chi2(target, scaled_to_target),
                    "Chi2AgainstK2": chi2(k2, scaled_to_target),
                    "CorrelationWithTarget": corr(target, scaled_to_target),
                    "CorrelationWithK2": corr(k2, scaled_to_target),
                    "RequiredScale": alpha_to_target,
                    "SignMatchesTargetAll": sign_matches(scaled_to_target, target),
                    "SignMatchesTargetStable": sign_matches(scaled_to_target, target, stable),
                    "StableRows": int(np.sum(stable)),
                    "ScaleFitAllowed": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "provisional_backreaction_preflight_no_measurement_validation",
                },
                {
                    "AuditID": "PROVISIONAL_BACKREACTION_PREFLIGHT_COMPARISON_V1",
                    "RouteID": route["RouteID"],
                    "ModelID": "BACKREACTION_FORBIDDEN_BEST_SCALE_TO_K2",
                    "ModelClass": "forbidden_k2_scale_diagnostic_only",
                    "Rows": len(target),
                    "Chi2AgainstTarget": chi2(target, scaled_to_k2),
                    "Chi2AgainstK2": chi2(k2, scaled_to_k2),
                    "CorrelationWithTarget": corr(target, scaled_to_k2),
                    "CorrelationWithK2": corr(k2, scaled_to_k2),
                    "RequiredScale": alpha_to_k2,
                    "SignMatchesTargetAll": sign_matches(scaled_to_k2, target),
                    "SignMatchesTargetStable": sign_matches(scaled_to_k2, target, stable),
                    "StableRows": int(np.sum(stable)),
                    "ScaleFitAllowed": False,
                    "MeasurementValidationAllowed": False,
                    "ClaimBoundary": "provisional_backreaction_preflight_no_measurement_validation",
                },
            ]
        )

        for i, row in vector.iterrows():
            row_rows.append(
                {
                    "AuditID": "PROVISIONAL_BACKREACTION_PREFLIGHT_ROW_AUDIT_V1",
                    "RouteID": route["RouteID"],
                    "ComponentIndex": i,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "OmegaInterpolated": float(omega_interp[i]),
                    "OmegaSigmaInterpolated": float(omega_sigma_interp[i]),
                    "BackreactionRawWhitened": float(omega_white_raw[i]),
                    "BackreactionUnitShapeWhitened": float(omega_shape_white[i]),
                    "WhitenedTarget": float(target[i]),
                    "K1Whitened": float(k1[i]),
                    "K2LockedWhitened": float(k2[i]),
                    "BackreactionRawResidualToTarget": float(target[i] - omega_white_raw[i]),
                    "BackreactionRawResidualToK2": float(k2[i] - omega_white_raw[i]),
                    "SignStable": bool(stable[i]),
                    "RawSignMatchesTarget": bool(np.sign(omega_white_raw[i]) == np.sign(target[i])),
                    "RawSignMatchesK2": bool(np.sign(omega_white_raw[i]) == np.sign(k2[i])),
                    "ClaimBoundary": "provisional_backreaction_preflight_no_measurement_validation",
                }
            )

        raw_score = [row for row in score_rows if row["RouteID"] == route["RouteID"] and row["ModelID"] == "BACKREACTION_RAW_INTERPOLATED"][-1]
        shape_score = [row for row in score_rows if row["RouteID"] == route["RouteID"] and row["ModelID"] == "BACKREACTION_UNIT_SHAPE"][-1]
        k2_chi2 = chi2(target, k2)
        k1_chi2 = chi2(target, k1)
        summary_rows.append(
            {
                "SummaryID": "PROVISIONAL_BACKREACTION_PREFLIGHT_COMPARISON_V1",
                "RouteID": route["RouteID"],
                "Rows": len(target),
                "RawBackreactionChi2": raw_score["Chi2AgainstTarget"],
                "ShapeBackreactionChi2": shape_score["Chi2AgainstTarget"],
                "K1Chi2": k1_chi2,
                "K2Chi2": k2_chi2,
                "DeltaChi2_K2_minus_RawBackreaction": k2_chi2 - float(raw_score["Chi2AgainstTarget"]),
                "DeltaChi2_K2_minus_ShapeBackreaction": k2_chi2 - float(shape_score["Chi2AgainstTarget"]),
                "RawCorrelationWithTarget": raw_score["CorrelationWithTarget"],
                "RawCorrelationWithK2": raw_score["CorrelationWithK2"],
                "RawStableSignMatches": raw_score["SignMatchesTargetStable"],
                "StableRows": raw_score["StableRows"],
                "ForbiddenScaleToTarget": alpha_to_target,
                "ForbiddenScaleToK2": alpha_to_k2,
                "AllowedForMeasurementValidation": False,
                "CurrentStatus": (
                    "PROVISIONAL_BACKREACTION_DOES_NOT_REPLACE_LOCKED_K2"
                    if k2_chi2 < float(raw_score["Chi2AgainstTarget"])
                    else "PROVISIONAL_BACKREACTION_COMPETITIVE_WARNING"
                ),
                "StrongestAllowedClaim": (
                    "the provisional BAO-only backreaction bridge is a sensitivity check and does not provide a source-native replacement for K2"
                ),
                "PrimaryResidualRisk": "backreaction observable-to-branch-contrast bridge is not source-native and any fitted scale is forbidden for claims",
                "ClaimBoundary": "provisional_backreaction_preflight_no_measurement_validation",
            }
        )

    row_audit = pd.DataFrame(row_rows)
    scorecard = pd.DataFrame(score_rows)
    summary = pd.DataFrame(summary_rows)
    row_audit.to_csv(OUT_ROW, index=False)
    scorecard.to_csv(OUT_SCORECARD, index=False)
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Provisional Backreaction Preflight Comparison",
        "",
        "Status: sensitivity bridge only; no measurement-validation claim.",
        "",
        "This audit interpolates the provisional BAO-only `Omega_R + 3 Omega_Q` curve onto the K2 route grids and compares raw/shape diagnostics with K1 and locked K2. The observable bridge is not source-native, so fitted bridge scales are reported only as forbidden diagnostics.",
        "",
        "## Outputs",
        "",
        f"- Row audit: `{OUT_ROW.relative_to(ROOT)}`",
        f"- Scorecard: `{OUT_SCORECARD.relative_to(ROOT)}`",
        f"- Summary: `{OUT_SUMMARY.relative_to(ROOT)}`",
        "",
        "## Claim Boundary",
        "",
        "This can weaken or motivate the backreaction route, but it cannot validate K2 or reject backreaction. Measurement validation remains closed.",
        "",
    ]
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_ROW}")
    print(f"Wrote {OUT_SCORECARD}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
