#!/usr/bin/env python3
"""Build raw public-observable preflight tables.

This script intentionally stops before finite-memory diagnostic construction.
It standardizes public BAO/SN inputs into a common row schema so the next stage
can define a registered diagnostic transform without making a measurement claim.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized, x_index_native, x_z_normalized
from fmc.public_data import (
    load_bao_mean,
    load_flat_covariance_with_size,
    load_manifest,
    load_pantheon_table,
    load_square_covariance,
    product_available,
)

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OUT_ROWS = ROOT / "evidence" / "public_diagnostic_transform_preflight.csv"
OUT_SUMMARY = ROOT / "evidence" / "public_diagnostic_transform_summary.csv"


def _coordinate_columns(z: np.ndarray) -> dict[str, np.ndarray]:
    return {
        "x_z_normalized": x_z_normalized(z),
        "x_chi_normalized": x_chi_normalized(z),
        "x_likelihood_native_index": x_index_native(len(z)),
    }


def _bao_rows(product: dict, root: Path) -> list[dict]:
    data_path = root / product["data_vector_path"]
    cov_path = root / product["covariance_path"]
    df = load_bao_mean(data_path)
    cov = load_square_covariance(cov_path)
    if len(df) != cov.shape[0]:
        raise ValueError(f"BAO data/covariance mismatch for {product['product_id']}")

    coords = _coordinate_columns(df["z"].to_numpy(float))
    sigma = np.sqrt(np.diag(cov))
    rows = []
    for i, item in df.reset_index(drop=True).iterrows():
        rows.append(
            {
                "ProductID": product["product_id"],
                "RowID": int(i),
                "ObservableClass": "BAO_RAW_OBSERVABLE",
                "Quantity": item["quantity"],
                "z": float(item["z"]),
                "Value": float(item["value"]),
                "SigmaDiag": float(sigma[i]),
                "CovarianceIndex": int(i),
                "x_z_normalized": float(coords["x_z_normalized"][i]),
                "x_chi_normalized": float(coords["x_chi_normalized"][i]),
                "x_likelihood_native_index": float(coords["x_likelihood_native_index"][i]),
                "TransformStatus": "RAW_OBSERVABLE_NOT_K2_DIAGNOSTIC",
                "DiagnosticTransformRequired": True,
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )
    return rows


def _pantheon_rows(product: dict, root: Path) -> list[dict]:
    data_path = root / product["data_vector_path"]
    cov_path = root / product["covariance_path"]
    df = load_pantheon_table(data_path).reset_index(drop=True)
    cov = load_flat_covariance_with_size(cov_path)
    if len(df) != cov.shape[0]:
        raise ValueError(f"Pantheon data/covariance mismatch for {product['product_id']}")

    z_col = "zHD" if "zHD" in df.columns else "zCMB"
    y_col = "MU_SH0ES" if "MU_SH0ES" in df.columns else "m_b_corr"
    coords = _coordinate_columns(df[z_col].to_numpy(float))
    sigma = np.sqrt(np.diag(cov))
    rows = []
    for i, item in df.iterrows():
        rows.append(
            {
                "ProductID": product["product_id"],
                "RowID": int(i),
                "ObservableClass": "SN_RAW_DISTANCE",
                "Quantity": y_col,
                "z": float(item[z_col]),
                "Value": float(item[y_col]),
                "SigmaDiag": float(sigma[i]),
                "CovarianceIndex": int(i),
                "x_z_normalized": float(coords["x_z_normalized"][i]),
                "x_chi_normalized": float(coords["x_chi_normalized"][i]),
                "x_likelihood_native_index": float(coords["x_likelihood_native_index"][i]),
                "TransformStatus": "RAW_OBSERVABLE_NOT_K2_DIAGNOSTIC",
                "DiagnosticTransformRequired": True,
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )
    return rows


def main() -> None:
    manifest = load_manifest(MANIFEST)
    rows = []
    for product in manifest.get("required_products", []):
        has_data, has_cov = product_available(product, ROOT)
        if not (has_data and has_cov):
            continue
        product_id = product.get("product_id", "")
        if product_id.startswith("DESI_"):
            rows.extend(_bao_rows(product, ROOT))
        elif product_id == "PANTHEON_PLUS_SH0ES_SN":
            rows.extend(_pantheon_rows(product, ROOT))

    df = pd.DataFrame(rows)
    df.to_csv(OUT_ROWS, index=False)

    summary = (
        df.groupby(["ProductID", "ObservableClass", "TransformStatus"], dropna=False)
        .agg(
            Rows=("RowID", "count"),
            ZMin=("z", "min"),
            ZMax=("z", "max"),
            MedianSigmaDiag=("SigmaDiag", "median"),
            DistinctQuantities=("Quantity", lambda values: "|".join(sorted(set(map(str, values))))),
        )
        .reset_index()
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
