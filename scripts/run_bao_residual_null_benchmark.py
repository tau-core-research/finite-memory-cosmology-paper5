#!/usr/bin/env python3
"""Run null comparators on the T1 BAO residual preflight vector."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.bao_transform import bao_log_residual_transform
from fmc.likelihood import aic, bic, chi2
from fmc.nulls import polynomial_fit, sign_randomized_control
from fmc.public_data import load_bao_mean, load_manifest, load_square_covariance, product_available

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OUT = ROOT / "evidence" / "bao_residual_null_benchmark.csv"
OUT_SCORECARD = ROOT / "evidence" / "bao_residual_null_scorecard.csv"


def _models(x: np.ndarray, y: np.ndarray) -> list[dict[str, object]]:
    return [
        {
            "ModelID": "ZERO_RESIDUAL_AUDIT_BASELINE",
            "Prediction": np.zeros_like(y),
            "ParameterCount": 0,
            "NullCategory": "fair_null",
            "Notes": "audit fiducial baseline residual equals zero",
        },
        {
            "ModelID": "CONSTANT_OFFSET",
            "Prediction": np.full_like(y, float(np.mean(y))),
            "ParameterCount": 1,
            "NullCategory": "diagnostic_control",
            "Notes": "unweighted constant residual offset",
        },
        {
            "ModelID": "POLY_DEG1",
            "Prediction": polynomial_fit(x, y, degree=1),
            "ParameterCount": 2,
            "NullCategory": "overfit_risk_control",
            "Notes": "fixed degree-1 smooth residual control",
        },
        {
            "ModelID": "POLY_DEG2",
            "Prediction": polynomial_fit(x, y, degree=2),
            "ParameterCount": 3,
            "NullCategory": "overfit_risk_control",
            "Notes": "fixed degree-2 smooth residual control",
        },
        {
            "ModelID": "SIGN_RANDOMIZED_CONTROL",
            "Prediction": sign_randomized_control(y, seed=1),
            "ParameterCount": 0,
            "NullCategory": "diagnostic_control",
            "Notes": "fixed-seed residual sign randomization",
        },
    ]


def _load_residual_product(product: dict) -> tuple[pd.DataFrame, np.ndarray]:
    mean = load_bao_mean(ROOT / product["data_vector_path"])
    cov = load_square_covariance(ROOT / product["covariance_path"])
    return bao_log_residual_transform(mean, cov, product["product_id"])


def main() -> None:
    manifest = load_manifest(MANIFEST)
    rows = []

    for product in manifest.get("required_products", []):
        product_id = product.get("product_id", "")
        if not product_id.startswith("DESI_"):
            continue
        has_data, has_cov = product_available(product, ROOT)
        if not (has_data and has_cov):
            continue

        df, cov = _load_residual_product(product)
        y = df["LogResidual"].to_numpy(float)
        n = len(y)

        for mapping_id in ["x_z_normalized", "x_chi_normalized", "x_likelihood_native_index"]:
            x = df[mapping_id].to_numpy(float)
            baseline_chi2 = None
            model_rows = []
            for model in _models(x, y):
                pred = np.asarray(model["Prediction"], dtype=float)
                c2 = chi2(y, pred, cov)
                if model["ModelID"] == "ZERO_RESIDUAL_AUDIT_BASELINE":
                    baseline_chi2 = c2
                model_rows.append((model, pred, c2))

            for model, pred, c2 in model_rows:
                residual = y - pred
                max_abs_resid_over_sigma = float(
                    np.max(np.abs(residual) / df["SigmaDiag"].to_numpy(float))
                )
                k = int(model["ParameterCount"])
                rows.append(
                    {
                        "ProductID": product_id,
                        "TransformID": "T1_BAO_DISTANCE_RATIO_RESIDUAL",
                        "MappingID": mapping_id,
                        "ModelID": model["ModelID"],
                        "NullCategory": model["NullCategory"],
                        "ParameterCount": k,
                        "Chi2FullCov": c2,
                        "AIC": aic(c2, k),
                        "BIC": bic(c2, k, n),
                        "DeltaChi2VsZeroResidual": c2 - float(baseline_chi2),
                        "MaxAbsResidualOverSigmaDiag": max_abs_resid_over_sigma,
                        "Rows": n,
                        "AllowedForMeasurementGate": False,
                        "Status": "BAO_RESIDUAL_PREFLIGHT_ONLY",
                        "Notes": model["Notes"],
                    }
                )

    result = pd.DataFrame(rows)
    result.to_csv(OUT, index=False)

    scorecard = (
        result.sort_values(["ProductID", "MappingID", "AIC"])
        .groupby(["ProductID", "MappingID"], as_index=False)
        .first()[
            [
                "ProductID",
                "MappingID",
                "ModelID",
                "NullCategory",
                "AIC",
                "BIC",
                "Chi2FullCov",
                "AllowedForMeasurementGate",
                "Status",
            ]
        ]
        .rename(columns={"ModelID": "BestAICModelID"})
    )
    scorecard.to_csv(OUT_SCORECARD, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SCORECARD}")


if __name__ == "__main__":
    main()
