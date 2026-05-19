#!/usr/bin/env python3
"""Export first reproducible L_SN and L_BAO transform matrices for A2 gate.

These matrices reproduce the current public-covariance proxy route. They are a
transform export, not an authorization for measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"

PANTHEON_TABLE = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = DATA / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_ROWS = EVIDENCE / "bao_residual_transform_preflight.csv"
BAO_COV = EVIDENCE / "bao_residual_transform_covariance.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
SN_BINS = EVIDENCE / "sn_residual_binned_preflight.csv"

OUT_DIR = DATA / "transforms"
OUT_SN = OUT_DIR / "k2_a2_l_sn_transform_v1.csv"
OUT_BAO = OUT_DIR / "k2_a2_l_bao_transform_v1.csv"
OUT_POLICY = EVIDENCE / "k2_a2_transform_matrix_policy_v1.csv"
OUT_READINESS = EVIDENCE / "k2_a2_transform_matrix_readiness_v1.csv"


def load_flat_covariance_with_size(path: Path) -> np.ndarray:
    values = np.loadtxt(path)
    declared = int(values[0])
    flat = values[1:]
    if len(flat) != declared * declared:
        raise ValueError(f"flat covariance length mismatch: declared={declared}, values={len(flat)}")
    return flat.reshape((declared, declared))


def grid_edges(grid: np.ndarray) -> np.ndarray:
    mids = (grid[:-1] + grid[1:]) / 2.0
    return np.concatenate([[max(0.0, grid[0] - (mids[0] - grid[0]))], mids, [grid[-1] + (grid[-1] - mids[-1])]])


def sn_bin_matrix(grid: np.ndarray, table: pd.DataFrame, covariance: np.ndarray) -> np.ndarray:
    z_col = "zHD" if "zHD" in table.columns else "zCMB"
    z = table[z_col].to_numpy(float)
    sigma_diag = np.sqrt(np.diag(covariance))
    weights_all = np.where(sigma_diag > 0.0, 1.0 / (sigma_diag * sigma_diag), 0.0)
    offset_weights = weights_all / float(np.sum(weights_all))
    centering = np.eye(len(table)) - np.ones((len(table), 1)) @ offset_weights.reshape(1, -1)

    edges = grid_edges(grid)
    bin_index = np.digitize(z, edges) - 1
    binner = np.zeros((len(grid), len(table)), dtype=float)
    for idx in range(len(grid)):
        members = np.where(bin_index == idx)[0]
        if len(members) == 0:
            continue
        weights = weights_all[members]
        denom = float(np.sum(weights))
        if denom <= 0.0:
            continue
        binner[idx, members] = weights / denom
    return binner @ centering


def load_bao_residual_covariance() -> tuple[pd.DataFrame, np.ndarray]:
    rows = pd.read_csv(BAO_ROWS)
    rows = rows[rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].reset_index(drop=True)
    cov_rows = pd.read_csv(BAO_COV)
    cov_rows = cov_rows[cov_rows["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].sort_values("CovRow")
    value_cols = [col for col in cov_rows.columns if col not in {"ProductID", "CovRow"}]
    return rows, cov_rows[value_cols].to_numpy(float)


def weighted_anchor_matrix(grid: np.ndarray, bao_rows: pd.DataFrame, bao_cov: np.ndarray) -> np.ndarray:
    z_bao = bao_rows["z"].to_numpy(float)
    sigma = np.sqrt(np.diag(bao_cov))
    matrix = np.zeros((len(grid), len(bao_rows)), dtype=float)
    for i, z in enumerate(grid):
        distances = np.abs(z_bao - float(z))
        nearest_distance = float(np.min(distances))
        members = np.where(distances == nearest_distance)[0]
        weights = np.where(sigma[members] > 0.0, 1.0 / (sigma[members] * sigma[members]), 0.0)
        denom = float(np.sum(weights))
        if denom <= 0.0:
            continue
        matrix[i, members] = weights / denom
    return matrix


def write_matrix(path: Path, matrix: np.ndarray, row_indices: list[int], prefix: str) -> None:
    df = pd.DataFrame(matrix, columns=[f"{prefix}_{i}" for i in range(matrix.shape[1])])
    df.insert(0, "GridIndex", row_indices)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
    grid = usable["z_grid"].to_numpy(float)
    grid_indices = usable["GridIndex"].astype(int).to_list()

    pantheon_table = pd.read_csv(PANTHEON_TABLE, sep=r"\s+", engine="python")
    pantheon_cov = load_flat_covariance_with_size(PANTHEON_COV)
    l_sn_raw = sn_bin_matrix(grid, pantheon_table, pantheon_cov)

    sn_bins = pd.read_csv(SN_BINS)
    sn_sigma = np.full(len(grid), np.nan)
    for local_i, grid_index in enumerate(grid_indices):
        match = sn_bins[sn_bins["GridIndex"].astype(int).eq(grid_index)]
        if not match.empty:
            sn_sigma[local_i] = float(match["SigmaDiagProxy"].iloc[0])
    d_sn = np.diag(np.where(np.isfinite(sn_sigma) & (sn_sigma > 0.0), 1.0 / sn_sigma, 0.0))
    l_sn = d_sn @ l_sn_raw

    bao_rows, bao_cov = load_bao_residual_covariance()
    l_bao_raw = weighted_anchor_matrix(grid, bao_rows, bao_cov)
    bao_sigma = np.sqrt(np.diag(l_bao_raw @ bao_cov @ l_bao_raw.T))
    d_bao = np.diag(np.where(bao_sigma > 0.0, 1.0 / bao_sigma, 0.0))
    l_bao = d_bao @ l_bao_raw

    write_matrix(OUT_SN, l_sn, grid_indices, "SN")
    write_matrix(OUT_BAO, l_bao, grid_indices, "BAO")

    policy = pd.DataFrame(
        [
            {
                "TransformMatrixID": "K2_A2_L_SN_V1",
                "MatrixPath": str(OUT_SN.relative_to(ROOT)),
                "Rows": l_sn.shape[0],
                "Columns": l_sn.shape[1],
                "InputProduct": "PANTHEON_PLUS_SH0ES_SN",
                "Definition": "weighted SN binning with global weighted centering and diagonal standardization",
                "Frozen": True,
                "LikelihoodNative": False,
                "AllowedForMeasurementValidation": False,
                "BlockingIssue": "nuisance_policy_and_full_likelihood_native_SN_definition_not_promoted",
                "ClaimBoundary": "transform_matrix_export_no_measurement_validation",
            },
            {
                "TransformMatrixID": "K2_A2_L_BAO_V1",
                "MatrixPath": str(OUT_BAO.relative_to(ROOT)),
                "Rows": l_bao.shape[0],
                "Columns": l_bao.shape[1],
                "InputProduct": "DESI_DR2_BAO_ALL_GAUSSIAN",
                "Definition": "nearest-redshift BAO anchor with inverse-variance weighting and diagonal standardization",
                "Frozen": True,
                "LikelihoodNative": False,
                "AllowedForMeasurementValidation": False,
                "BlockingIssue": "bao_observable_prediction_policy_and_full_likelihood_native_definition_not_promoted",
                "ClaimBoundary": "transform_matrix_export_no_measurement_validation",
            },
        ]
    )
    policy.to_csv(OUT_POLICY, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "K2_A2_TRANSFORM_MATRIX_V1_READINESS",
                "LSNExported": OUT_SN.exists(),
                "LBAOExported": OUT_BAO.exists(),
                "Rows": len(grid_indices),
                "SNColumns": l_sn.shape[1],
                "BAOColumns": l_bao.shape[1],
                "TransformMatricesFrozen": True,
                "AllowedForMeasurementValidation": False,
                "CurrentStatus": "EXPORTED_PREFLIGHT_TRANSFORMS_NOT_FULL_LIKELIHOOD_NATIVE",
                "BlockingIssue": "SN_and_BAO_transforms_are_reproducible_but_not_promoted_to_full_likelihood_native",
                "NextAction": "freeze nuisance/baseline/cross-covariance/K1/null policies before full scorecard",
                "ClaimBoundary": "transform_matrix_export_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)

    print(f"Wrote {OUT_SN}")
    print(f"Wrote {OUT_BAO}")
    print(f"Wrote {OUT_POLICY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
