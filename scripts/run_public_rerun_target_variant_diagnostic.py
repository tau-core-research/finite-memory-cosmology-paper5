#!/usr/bin/env python3
"""Score target-construction variants for the public rerun.

These variants are diagnostics only. They are not promoted measurement routes
and do not authorize changing locked A2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.likelihood import aic, bic, chi2

EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

RERUN = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COV = EVIDENCE / "likelihood_native_rerun_candidate_covariance.csv"
BRANCH = EVIDENCE / "public_rerun_branch_contribution_audit.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
K2 = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT_SCORE = EVIDENCE / "public_rerun_target_variant_scorecard.csv"
OUT_SUMMARY = EVIDENCE / "public_rerun_target_variant_summary.csv"


def load_covariance(grid: list[int]) -> np.ndarray:
    cov = pd.read_csv(COV)
    return cov[[str(i) for i in grid]].to_numpy(float)


def model_predictions(x: np.ndarray, y: np.ndarray, k1: np.ndarray, k2: np.ndarray) -> list[tuple[str, np.ndarray, int, str]]:
    rows: list[tuple[str, np.ndarray, int, str]] = [
        ("K1_NO_MEMORY", k1, 0, "fair_null"),
        ("K2_LOCKED_A2_UNCHANGED", k2, 0, "locked_prediction"),
        ("ZERO_RESPONSE_CONTROL", np.zeros_like(y), 0, "diagnostic_control"),
    ]
    for degree in [2, 3]:
        coeff = np.polyfit(x, y, degree)
        rows.append((f"POLY_DEG{degree}", np.polyval(coeff, x), degree + 1, "overfit_risk_control"))
    return rows


def score_variant(
    variant_id: str,
    variant_class: str,
    y: np.ndarray,
    x: np.ndarray,
    cov: np.ndarray,
    k1: np.ndarray,
    k2: np.ndarray,
) -> list[dict[str, object]]:
    rows = []
    for model_id, pred, k, model_class in model_predictions(x, y, k1, k2):
        c2 = chi2(y, pred, cov)
        rows.append(
            {
                "VariantID": variant_id,
                "VariantClass": variant_class,
                "ModelID": model_id,
                "ModelClass": model_class,
                "Rows": len(y),
                "ParameterCount": k,
                "Chi2": c2,
                "AIC": aic(c2, k),
                "BIC": bic(c2, k, len(y)),
                "MeanAbsResidual": float(np.mean(np.abs(y - pred))),
                "CounterfactualOnly": variant_id != "RAW_PROJECTED_SN_MINUS_BAO_CURRENT",
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "public_rerun_target_variant_diagnostic_no_measurement_validation",
            }
        )
    return rows


def main() -> None:
    rerun = pd.read_csv(RERUN).sort_values("GridIndex").reset_index(drop=True)
    branch = pd.read_csv(BRANCH).sort_values("GridIndex").reset_index(drop=True)
    k1 = pd.read_csv(K1).set_index("GridIndex")
    k2 = pd.read_csv(K2).set_index("GridIndex")

    grid = rerun["GridIndex"].astype(int).to_list()
    cov = load_covariance(grid)
    x = rerun["x_coordinate"].to_numpy(float)
    k1_pred = np.array([float(k1.loc[i, "K1Response"]) for i in grid])
    k2_pred = np.array([float(k2.loc[i, "K2SourceSplitA2Prediction"]) for i in grid])

    sn_raw = branch["SNComponentRawProjected"].to_numpy(float)
    bao_raw = branch["BAOComponentLogProjected"].to_numpy(float)
    coord = branch["CoordinateNativeTarget"].to_numpy(float)
    sn_std = branch["SNStandardizedResidual"].to_numpy(float)
    bao_std = branch["BAOStandardizedResidual"].to_numpy(float)

    variants = {
        "RAW_PROJECTED_SN_MINUS_BAO_CURRENT": (
            "current_candidate",
            sn_raw - bao_raw,
        ),
        "RAW_PROJECTED_SN_PLUS_BAO_SIGN_FLIP_CHECK": (
            "sign_convention_counterfactual",
            sn_raw + bao_raw,
        ),
        "STANDARDIZED_SN_MINUS_BAO_COORDINATE_TARGET": (
            "standardized_counterfactual",
            coord,
        ),
        "STANDARDIZED_SN_PLUS_BAO_SIGN_FLIP_CHECK": (
            "standardized_sign_counterfactual",
            sn_std + bao_std,
        ),
        "RAW_PROJECTED_SIGN_ALIGNED_TO_STANDARDIZED": (
            "sign_alignment_counterfactual",
            np.sign(coord) * np.abs(sn_raw - bao_raw),
        ),
        "RAW_PROJECTED_MAGNITUDE_WITH_STANDARDIZED_SIGN_AND_SCALE": (
            "scale_alignment_counterfactual",
            coord,
        ),
    }

    score_rows: list[dict[str, object]] = []
    for variant_id, (variant_class, y) in variants.items():
        score_rows.extend(score_variant(variant_id, variant_class, y, x, cov, k1_pred, k2_pred))
    score = pd.DataFrame(score_rows)
    score.to_csv(OUT_SCORE, index=False)

    summary_rows = []
    for variant_id, group in score.groupby("VariantID", sort=False):
        k2_row = group[group["ModelID"].eq("K2_LOCKED_A2_UNCHANGED")].iloc[0]
        k1_row = group[group["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        poly = group[group["ModelID"].str.startswith("POLY")]
        best_poly = poly.sort_values("AIC").iloc[0]
        best = group.sort_values("AIC").iloc[0]
        summary_rows.append(
            {
                "VariantID": variant_id,
                "VariantClass": k2_row["VariantClass"],
                "BestModel": best["ModelID"],
                "K1AIC": k1_row["AIC"],
                "K2AIC": k2_row["AIC"],
                "BestPolyID": best_poly["ModelID"],
                "BestPolyAIC": best_poly["AIC"],
                "DeltaAIC_K2_minus_K1": float(k2_row["AIC"] - k1_row["AIC"]),
                "DeltaAIC_K2_minus_BestPoly": float(k2_row["AIC"] - best_poly["AIC"]),
                "K2ImprovesOverK1": bool(k2_row["AIC"] < k1_row["AIC"]),
                "K2BeatsBestPoly": bool(k2_row["AIC"] < best_poly["AIC"]),
                "CounterfactualOnly": bool(k2_row["CounterfactualOnly"]),
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": "public_rerun_target_variant_diagnostic_no_measurement_validation",
            }
        )
    summary = pd.DataFrame(summary_rows)

    current = summary[summary["VariantID"].eq("RAW_PROJECTED_SN_MINUS_BAO_CURRENT")].iloc[0]
    counter = summary[summary["CounterfactualOnly"].astype(bool)]
    k2_vs_k1_counter = int(counter["K2ImprovesOverK1"].sum())
    k2_vs_poly_counter = int(counter["K2BeatsBestPoly"].sum())
    overview = pd.DataFrame(
        [
            {
                "VariantID": "TARGET_VARIANT_DIAGNOSTIC_OVERVIEW",
                "VariantClass": "overview",
                "BestModel": "",
                "K1AIC": np.nan,
                "K2AIC": np.nan,
                "BestPolyID": "",
                "BestPolyAIC": np.nan,
                "DeltaAIC_K2_minus_K1": current["DeltaAIC_K2_minus_K1"],
                "DeltaAIC_K2_minus_BestPoly": current["DeltaAIC_K2_minus_BestPoly"],
                "K2ImprovesOverK1": current["K2ImprovesOverK1"],
                "K2BeatsBestPoly": current["K2BeatsBestPoly"],
                "CounterfactualOnly": True,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "TARGET_VARIANTS_ARE_CONVENTION_SENSITIVE_NO_PROMOTION",
                "CounterfactualVariantsK2OverK1": k2_vs_k1_counter,
                "CounterfactualVariantsK2OverPoly": k2_vs_poly_counter,
                "CounterfactualVariants": len(counter),
                "StrongestAllowedClaim": "target-construction variants materially change K2-vs-null status, so target convention must be frozen before interpretation",
                "NextAction": "select a physics/statistics-justified target convention before any further A2 score interpretation",
                "ClaimBoundary": "public_rerun_target_variant_diagnostic_no_measurement_validation",
            }
        ]
    )
    pd.concat([overview, summary], ignore_index=True).to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_SCORE}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
