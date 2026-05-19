#!/usr/bin/env python3
"""Validate downloaded public benchmark input shapes."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.public_data import load_manifest, product_available, validate_product_entry

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OUT = ROOT / "evidence" / "public_input_inventory.csv"


def _load_bao_mean(path: Path) -> tuple[int, list[str], float, float]:
    df = pd.read_csv(
        path,
        sep=r"\s+",
        comment="#",
        names=["z", "value", "quantity"],
        engine="python",
    )
    return (
        int(len(df)),
        sorted(df["quantity"].dropna().astype(str).unique().tolist()),
        float(df["z"].min()),
        float(df["z"].max()),
    )


def _load_square_cov(path: Path) -> tuple[int, int, bool]:
    cov = np.loadtxt(path)
    if cov.ndim != 2:
        return int(cov.shape[0]), 0, False
    rows, cols = cov.shape
    return int(rows), int(cols), bool(rows == cols)


def _load_pantheon_data(path: Path) -> tuple[int, list[str], float, float]:
    df = pd.read_csv(path, sep=r"\s+", engine="python")
    z_col = "zHD" if "zHD" in df.columns else "zCMB"
    return int(len(df)), list(df.columns), float(df[z_col].min()), float(df[z_col].max())


def _pantheon_cov_shape(path: Path) -> tuple[int, int, bool]:
    with path.open("r", encoding="utf-8") as handle:
        first = handle.readline().strip()
        declared = int(first)
        values = sum(1 for _ in handle)
    return declared, values, bool(values == declared * declared)


def main() -> None:
    manifest = load_manifest(MANIFEST)
    rows = []

    for product in manifest.get("required_products", []):
        product_id = product.get("product_id", "")
        issues = validate_product_entry(product)
        has_data, has_cov = product_available(product, ROOT)
        data_path = ROOT / product["data_vector_path"] if product.get("data_vector_path") else None
        cov_path = ROOT / product["covariance_path"] if product.get("covariance_path") else None

        row = {
            "ProductID": product_id,
            "Required": bool(product.get("required", False)),
            "HasDataVector": bool(has_data),
            "HasCovariance": bool(has_cov),
            "DataRows": "",
            "CovRows": "",
            "CovColsOrFlatValues": "",
            "CovSquareOrDeclaredComplete": "",
            "DataCovDimensionMatch": "",
            "ZMin": "",
            "ZMax": "",
            "QuantitiesOrColumns": "",
            "ValidationIssue": ";".join(issues),
            "NextAction": product.get("next_action", ""),
        }

        if not (has_data and has_cov and data_path is not None and cov_path is not None):
            rows.append(row)
            continue

        if product_id.startswith("DESI_"):
            data_rows, quantities, z_min, z_max = _load_bao_mean(data_path)
            cov_rows, cov_cols, cov_square = _load_square_cov(cov_path)
            row.update(
                {
                    "DataRows": data_rows,
                    "CovRows": cov_rows,
                    "CovColsOrFlatValues": cov_cols,
                    "CovSquareOrDeclaredComplete": cov_square,
                    "DataCovDimensionMatch": bool(data_rows == cov_rows == cov_cols),
                    "ZMin": z_min,
                    "ZMax": z_max,
                    "QuantitiesOrColumns": "|".join(quantities),
                }
            )
        elif product_id == "PANTHEON_PLUS_SH0ES_SN":
            data_rows, columns, z_min, z_max = _load_pantheon_data(data_path)
            declared, flat_values, complete = _pantheon_cov_shape(cov_path)
            row.update(
                {
                    "DataRows": data_rows,
                    "CovRows": declared,
                    "CovColsOrFlatValues": flat_values,
                    "CovSquareOrDeclaredComplete": complete,
                    "DataCovDimensionMatch": bool(data_rows == declared and complete),
                    "ZMin": z_min,
                    "ZMax": z_max,
                    "QuantitiesOrColumns": "|".join(columns[:12]),
                }
            )

        rows.append(row)

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
