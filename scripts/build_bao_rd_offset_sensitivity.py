#!/usr/bin/env python3
"""Build a non-eligible BAO sensitivity transform with rd offset absorbed."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.bao_transform import FIDUCIAL_AUDIT_BASELINE, bao_log_residual_transform
from fmc.likelihood import aic, bic, chi2
from fmc.public_data import load_bao_mean, load_manifest, load_square_covariance, product_available

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
OFFSET = ROOT / "evidence" / "bao_baseline_offset_diagnosis.csv"
OUT_ROWS = ROOT / "evidence" / "bao_rd_offset_sensitivity_preflight.csv"
OUT_SUMMARY = ROOT / "evidence" / "bao_rd_offset_sensitivity_summary.csv"


def _offset_baseline(product_id: str, offsets: pd.DataFrame) -> dict:
    row = offsets[offsets["ProductID"] == product_id]
    if row.empty:
        raise ValueError(f"missing offset diagnosis for {product_id}")
    rd = float(row.iloc[0]["EffectiveRdMpcIfAbsorbed"])
    baseline = dict(FIDUCIAL_AUDIT_BASELINE)
    baseline["baseline_id"] = "AUDIT_RD_OFFSET_ABSORBED_V0"
    baseline["rd_mpc"] = rd
    return baseline


def main() -> None:
    manifest = load_manifest(MANIFEST)
    offsets = pd.read_csv(OFFSET)
    row_blocks = []
    summary_rows = []

    for product in manifest.get("required_products", []):
        product_id = product.get("product_id", "")
        if not product_id.startswith("DESI_"):
            continue
        has_data, has_cov = product_available(product, ROOT)
        if not (has_data and has_cov):
            continue

        baseline = _offset_baseline(product_id, offsets)
        mean = load_bao_mean(ROOT / product["data_vector_path"])
        cov = load_square_covariance(ROOT / product["covariance_path"])
        rows, residual_cov = bao_log_residual_transform(mean, cov, product_id, baseline=baseline)
        rows["TransformStatus"] = "RD_OFFSET_SENSITIVITY_NOT_MEASUREMENT_GATE"
        rows["ClaimBoundary"] = "same_data_scale_absorption_sensitivity_only"
        row_blocks.append(rows)

        y = rows["LogResidual"].to_numpy(float)
        zero = np.zeros_like(y)
        c2 = chi2(y, zero, residual_cov)
        summary_rows.append(
            {
                "ProductID": product_id,
                "BaselineID": baseline["baseline_id"],
                "RdMpc": baseline["rd_mpc"],
                "Rows": len(rows),
                "MeanAbsLogResidual": float(np.mean(np.abs(y))),
                "MaxAbsLogResidual": float(np.max(np.abs(y))),
                "Chi2ZeroResidual": c2,
                "AICZeroResidual": aic(c2, 1),
                "BICZeroResidual": bic(c2, 1, len(rows)),
                "ParameterCount": 1,
                "AllowedForMeasurementGate": False,
                "BlockingIssue": "rd_absorbed_from_same_data_offset;not_likelihood_native;not_coordinate_native",
                "Interpretation": "sensitivity_check_for_baseline_scale_offset_not_finite_memory_signal",
            }
        )

    pd.concat(row_blocks, ignore_index=True).to_csv(OUT_ROWS, index=False)
    pd.DataFrame(summary_rows).to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
