#!/usr/bin/env python3
"""Build Pantheon+ SN residual preflight outputs.

This is a source-split transform-development artifact. It is not a K2 scoring
target because the centered residual subtracts a same-sample offset.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.public_data import load_flat_covariance_with_size, load_manifest, load_pantheon_table
from fmc.sn_transform import bin_sn_residuals_to_grid, sn_residual_transform

MANIFEST = ROOT / "data" / "public_ingest_manifest.yaml"
DIAG_PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
OUT_ROWS = ROOT / "evidence" / "sn_residual_preflight.csv"
OUT_BINS = ROOT / "evidence" / "sn_residual_binned_preflight.csv"
OUT_SUMMARY = ROOT / "evidence" / "sn_residual_preflight_summary.csv"


def pantheon_product() -> dict:
    manifest = load_manifest(MANIFEST)
    for product in manifest.get("required_products", []):
        if product.get("product_id") == "PANTHEON_PLUS_SH0ES_SN":
            return product
    raise ValueError("PANTHEON_PLUS_SH0ES_SN is missing from manifest")


def main() -> None:
    product = pantheon_product()
    table = load_pantheon_table(ROOT / product["data_vector_path"])
    covariance = load_flat_covariance_with_size(ROOT / product["covariance_path"])
    rows = sn_residual_transform(table, covariance, product["product_id"])
    rows.to_csv(OUT_ROWS, index=False)

    grid = pd.read_csv(DIAG_PACKET)["z"].to_numpy(float)
    binned = bin_sn_residuals_to_grid(rows, grid)
    binned.to_csv(OUT_BINS, index=False)

    summary_rows = [
        {
            "ArtifactID": "SN_RAW_RESIDUAL_PREFLIGHT",
            "Rows": len(rows),
            "ZMin": rows["z"].min(),
            "ZMax": rows["z"].max(),
            "MeanRawResidualMu": rows["RawResidualMu"].mean(),
            "MedianRawResidualMu": rows["RawResidualMu"].median(),
            "SameSampleOffsetMu": rows["SameSampleOffsetMu"].iloc[0],
            "MeanCenteredResidualMu": rows["CenteredResidualMu"].mean(),
            "MedianSigmaDiag": rows["SigmaDiag"].median(),
            "Status": "PREFLIGHT_ONLY_NOT_MEASUREMENT_GATE",
            "BlockingIssue": "same_sample_offset_not_k1_target;no_source_split_joint_covariance",
            "NextAction": "Define source-split coordinate-native K1 target and joint covariance before K2 scoring.",
        },
        {
            "ArtifactID": "SN_BINNED_TO_CURRENT_GRID_PREFLIGHT",
            "Rows": len(binned),
            "ZMin": binned["z_grid"].min() if not binned.empty else None,
            "ZMax": binned["z_grid"].max() if not binned.empty else None,
            "MeanRawResidualMu": binned["RawResidualMeanMu"].mean() if not binned.empty else None,
            "MedianRawResidualMu": binned["RawResidualMeanMu"].median() if not binned.empty else None,
            "SameSampleOffsetMu": rows["SameSampleOffsetMu"].iloc[0],
            "MeanCenteredResidualMu": binned["CenteredResidualMeanMu"].mean() if not binned.empty else None,
            "MedianSigmaDiag": binned["SigmaDiagProxy"].median() if not binned.empty else None,
            "Status": "PREFLIGHT_ONLY_NOT_MEASUREMENT_GATE",
            "BlockingIssue": "binned_diagonal_proxy_only;not_joint_sn_bao_reconstruction",
            "NextAction": "Use as transform-development evidence only.",
        },
    ]
    pd.DataFrame(summary_rows).to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_ROWS}")
    print(f"Wrote {OUT_BINS}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
