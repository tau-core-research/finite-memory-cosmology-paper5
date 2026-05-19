#!/usr/bin/env python3
"""Build the T1 BAO residual preflight transform."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.bao_transform import FIDUCIAL_AUDIT_BASELINE, bao_log_residual_transform
from fmc.public_data import load_bao_mean, load_manifest, load_square_covariance, product_available

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OUT_ROWS = ROOT / "evidence" / "bao_residual_transform_preflight.csv"
OUT_SUMMARY = ROOT / "evidence" / "bao_residual_transform_summary.csv"
OUT_COV = ROOT / "evidence" / "bao_residual_transform_covariance.csv"


def main() -> None:
    manifest = load_manifest(MANIFEST)
    all_rows = []
    covariance_blocks = []

    for product in manifest.get("required_products", []):
        product_id = product.get("product_id", "")
        if not product_id.startswith("DESI_"):
            continue
        has_data, has_cov = product_available(product, ROOT)
        if not (has_data and has_cov):
            continue

        mean = load_bao_mean(ROOT / product["data_vector_path"])
        cov = load_square_covariance(ROOT / product["covariance_path"])
        rows, residual_cov = bao_log_residual_transform(mean, cov, product_id)
        all_rows.append(rows)

        cov_df = pd.DataFrame(residual_cov)
        cov_df.insert(0, "CovRow", np.arange(len(cov_df), dtype=int))
        cov_df.insert(0, "ProductID", product_id)
        covariance_blocks.append(cov_df)

    if not all_rows:
        raise RuntimeError("No DESI BAO products were available for T1 preflight")

    df = pd.concat(all_rows, ignore_index=True)
    df.to_csv(OUT_ROWS, index=False)

    summary = (
        df.groupby(["ProductID", "TransformID", "TransformStatus", "BaselineID"], dropna=False)
        .agg(
            Rows=("RowID", "count"),
            ZMin=("z", "min"),
            ZMax=("z", "max"),
            MeanAbsLogResidual=("LogResidual", lambda values: float(np.mean(np.abs(values)))),
            MaxAbsLogResidual=("LogResidual", lambda values: float(np.max(np.abs(values)))),
            MedianSigmaDiag=("SigmaDiag", "median"),
        )
        .reset_index()
    )
    summary["BaselineH0"] = FIDUCIAL_AUDIT_BASELINE["H0"]
    summary["BaselineOmegaM"] = FIDUCIAL_AUDIT_BASELINE["omega_m"]
    summary["BaselineRdMpc"] = FIDUCIAL_AUDIT_BASELINE["rd_mpc"]
    summary["AllowedForMeasurementGate"] = False
    summary["BlockingIssue"] = "audit_fiducial_baseline_not_likelihood_native;k1_baseline_not_exported;null_benchmark_not_run"
    summary.to_csv(OUT_SUMMARY, index=False)

    pd.concat(covariance_blocks, ignore_index=True).to_csv(OUT_COV, index=False)
    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_COV}")


if __name__ == "__main__":
    main()
