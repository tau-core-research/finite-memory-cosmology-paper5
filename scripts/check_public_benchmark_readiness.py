#!/usr/bin/env python3
"""Check readiness for a Phase II public benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.public_data import load_manifest, product_available, validate_product_entry

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OUT = ROOT / "evidence" / "public_benchmark_readiness.csv"


def main() -> None:
    manifest = load_manifest(MANIFEST)
    rows = []
    for product in manifest.get("required_products", []):
        has_data, has_cov = product_available(product, ROOT)
        issues = validate_product_entry(product)
        has_mapping = bool(product.get("coordinate_mapping"))
        has_null = bool(product.get("null_comparators"))
        blocking = []
        if product.get("required", False) and not has_data:
            blocking.append("data_vector_unavailable")
        if product.get("required", False) and not has_cov:
            blocking.append("covariance_unavailable")
        if product.get("required", False) and not has_mapping:
            blocking.append("coordinate_mapping_unset")
        if product.get("required", False) and not has_null:
            blocking.append("null_comparators_unset")
        blocking.extend(issues)
        rows.append(
            {
                "ProductID": product.get("product_id", ""),
                "Required": bool(product.get("required", False)),
                "Available": bool(has_data and has_cov and has_mapping and has_null),
                "HasDataVector": bool(has_data),
                "HasCovariance": bool(has_cov),
                "HasCoordinateMapping": bool(has_mapping),
                "HasNullComparator": bool(has_null),
                "CandidateDataURL": product.get("candidate_data_url", ""),
                "CandidateCovarianceURL": product.get("candidate_covariance_url", ""),
                "SourceDocumentURL": product.get("source_document_url", ""),
                "BlockingIssue": ";".join(dict.fromkeys(blocking)) if blocking else "",
                "NextAction": product.get("next_action", ""),
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
