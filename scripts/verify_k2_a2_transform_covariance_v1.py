#!/usr/bin/env python3
"""Verify the exported K2 A2 transform matrices against the covariance proxy.

This is a preflight consistency check only. It verifies that the frozen
L_SN/L_BAO matrices reproduce the current public covariance proxy route; it
does not promote the result to a measurement-validation likelihood.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.public_data import load_flat_covariance_with_size

SN_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_COV = ROOT / "evidence" / "bao_residual_transform_covariance.csv"
L_SN = ROOT / "data" / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = ROOT / "data" / "transforms" / "k2_a2_l_bao_transform_v1.csv"
REFERENCE = ROOT / "evidence" / "source_split_likelihood_native_public_covariance_proxy.csv"

OUT_COV = ROOT / "evidence" / "k2_a2_transform_propagated_covariance_v1.csv"
OUT_SUMMARY = ROOT / "evidence" / "k2_a2_transform_covariance_verification_v1.csv"


def load_transform(path: Path) -> tuple[list[int], np.ndarray]:
    df = pd.read_csv(path)
    grid = df["GridIndex"].astype(int).to_list()
    matrix = df.drop(columns=["GridIndex"]).to_numpy(float)
    return grid, matrix


def load_bao_covariance(path: Path) -> np.ndarray:
    rows = pd.read_csv(path)
    rows = rows[rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].sort_values("CovRow")
    value_cols = [col for col in rows.columns if col not in {"ProductID", "CovRow"}]
    return rows[value_cols].to_numpy(float)


def load_reference(path: Path, grid: list[int]) -> np.ndarray:
    df = pd.read_csv(path)
    df = df[df["CovarianceID"].eq("PUBLIC_SN_BAO_PROPAGATED_PROXY_V1")].copy()
    df["GridIndex"] = df["GridIndex"].astype(int)
    df = df.set_index("GridIndex").loc[grid]
    return df[[str(idx) for idx in grid]].to_numpy(float)


def main() -> None:
    sn_grid, l_sn = load_transform(L_SN)
    bao_grid, l_bao = load_transform(L_BAO)
    if sn_grid != bao_grid:
        raise ValueError("SN and BAO transform grids differ")

    pantheon_cov = load_flat_covariance_with_size(SN_COV)
    bao_cov = load_bao_covariance(BAO_COV)

    propagated = l_sn @ pantheon_cov @ l_sn.T + l_bao @ bao_cov @ l_bao.T
    reference = load_reference(REFERENCE, sn_grid)
    diff = propagated - reference

    cov_df = pd.DataFrame(propagated, columns=[str(idx) for idx in sn_grid])
    cov_df.insert(0, "GridIndex", sn_grid)
    cov_df.insert(0, "CovarianceID", "K2_A2_TRANSFORM_PROPAGATED_PROXY_V1")
    cov_df["CovarianceStatus"] = "transform_propagated_prefight_not_full_likelihood"
    cov_df["ClaimBoundary"] = "transform_covariance_verification_no_measurement_validation"
    cov_df.to_csv(OUT_COV, index=False)

    max_abs = float(np.max(np.abs(diff)))
    rms = float(np.sqrt(np.mean(diff * diff)))
    summary = pd.DataFrame(
        [
            {
                "VerificationID": "K2_A2_TRANSFORM_COVARIANCE_V1",
                "Rows": len(sn_grid),
                "SNColumns": l_sn.shape[1],
                "BAOColumns": l_bao.shape[1],
                "ReferenceCovarianceID": "PUBLIC_SN_BAO_PROPAGATED_PROXY_V1",
                "MaxAbsDifferenceVsReference": max_abs,
                "RMSDifferenceVsReference": rms,
                "MatchesReferenceWithinTolerance": max_abs <= 1e-10,
                "SNBAOCrossCovarianceIncluded": False,
                "AllowedForMeasurementValidation": False,
                "CurrentStatus": (
                    "TRANSFORM_REPRODUCES_PUBLIC_PROXY"
                    if max_abs <= 1e-10
                    else "TRANSFORM_REFERENCE_MISMATCH"
                ),
                "BlockingIssue": (
                    "none_for_preflight_reproduction;cross_covariance_and_likelihood_native_policies_still_missing"
                    if max_abs <= 1e-10
                    else "exported_transform_does_not_reproduce_existing_public_covariance_proxy"
                ),
                "NextAction": "freeze nuisance/cross-covariance/K1/null policies before full measurement gate",
                "ClaimBoundary": "transform_covariance_verification_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT_COV}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
