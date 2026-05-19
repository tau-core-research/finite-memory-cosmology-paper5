"""SN residual transform helpers for source-split preflight."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fmc.bao_transform import comoving_distance_mpc
from fmc.coordinates import x_chi_normalized, x_index_native, x_z_normalized


SN_AUDIT_BASELINE = {
    "baseline_id": "AUDIT_FLAT_LCDM_SN_V0",
    "H0": 70.0,
    "omega_m": 0.3,
}


def luminosity_distance_mpc(z, h0: float = 70.0, omega_m: float = 0.3) -> np.ndarray:
    """Flat-audit luminosity distance in Mpc."""
    z_values = np.asarray(z, dtype=float)
    return (1.0 + z_values) * comoving_distance_mpc(z_values, h0=h0, omega_m=omega_m)


def distance_modulus_prediction(z, baseline: dict | None = None) -> np.ndarray:
    """Distance-modulus prediction under the audit flat-LCDM baseline."""
    params = baseline or SN_AUDIT_BASELINE
    dl = luminosity_distance_mpc(
        z,
        h0=float(params["H0"]),
        omega_m=float(params["omega_m"]),
    )
    return 5.0 * np.log10(np.maximum(dl, 1e-12)) + 25.0


def inverse_variance_offset(residual, sigma) -> float:
    """Best constant offset under a diagonal covariance proxy."""
    r = np.asarray(residual, dtype=float)
    s = np.asarray(sigma, dtype=float)
    weights = np.where(s > 0.0, 1.0 / (s * s), 0.0)
    denom = float(np.sum(weights))
    if denom <= 0.0:
        return 0.0
    return float(np.sum(weights * r) / denom)


def sn_residual_transform(
    table: pd.DataFrame,
    covariance: np.ndarray,
    product_id: str,
    baseline: dict | None = None,
) -> pd.DataFrame:
    """Return SN residual rows for transform preflight.

    The centered residual subtracts a same-sample constant offset and is marked
    as preflight only. It must not be used as a measurement-gate K1 target.
    """
    if len(table) != covariance.shape[0] or covariance.shape[0] != covariance.shape[1]:
        raise ValueError("SN data/covariance dimensions do not match")

    params = baseline or SN_AUDIT_BASELINE
    df = table.reset_index(drop=True).copy()
    z_col = "zHD" if "zHD" in df.columns else "zCMB"
    mu_col = "MU_SH0ES" if "MU_SH0ES" in df.columns else "m_b_corr"
    z = df[z_col].to_numpy(float)
    observed = df[mu_col].to_numpy(float)
    predicted = distance_modulus_prediction(z, params)
    sigma = np.sqrt(np.diag(covariance))
    raw_residual = observed - predicted
    offset = inverse_variance_offset(raw_residual, sigma)
    centered_residual = raw_residual - offset
    coords = {
        "x_z_normalized": x_z_normalized(z),
        "x_chi_normalized": x_chi_normalized(z),
        "x_likelihood_native_index": x_index_native(len(df)),
    }

    return pd.DataFrame(
        {
            "TransformID": "T2_SN_DISTANCE_MODULUS_RESIDUAL",
            "ProductID": product_id,
            "RowID": np.arange(len(df), dtype=int),
            "z": z,
            "ObservedMu": observed,
            "AuditPredictionMu": predicted,
            "RawResidualMu": raw_residual,
            "SameSampleOffsetMu": offset,
            "CenteredResidualMu": centered_residual,
            "SigmaDiag": sigma,
            "CovarianceIndex": np.arange(len(df), dtype=int),
            "x_z_normalized": coords["x_z_normalized"],
            "x_chi_normalized": coords["x_chi_normalized"],
            "x_likelihood_native_index": coords["x_likelihood_native_index"],
            "BaselineID": params["baseline_id"],
            "TransformStatus": "SN_RESIDUAL_PREFLIGHT_NOT_MEASUREMENT_GATE",
            "ClaimBoundary": "preflight_only_same_sample_offset_not_k1_target",
        }
    )


def bin_sn_residuals_to_grid(rows: pd.DataFrame, grid_z) -> pd.DataFrame:
    """Bin centered SN residuals to a reference redshift grid using diagonal weights."""
    grid = np.asarray(grid_z, dtype=float)
    mids = (grid[:-1] + grid[1:]) / 2.0
    edges = np.concatenate(
        [
            [max(0.0, grid[0] - (mids[0] - grid[0]))],
            mids,
            [grid[-1] + (grid[-1] - mids[-1])],
        ]
    )
    df = rows.copy()
    df["GridIndex"] = np.digitize(df["z"].to_numpy(float), edges) - 1
    df = df[(df["GridIndex"] >= 0) & (df["GridIndex"] < len(grid))].copy()

    binned = []
    for idx, group in df.groupby("GridIndex", sort=True):
        sigma = group["SigmaDiag"].to_numpy(float)
        weights = np.where(sigma > 0.0, 1.0 / (sigma * sigma), 0.0)
        denom = float(np.sum(weights))
        if denom <= 0.0:
            continue
        centered = group["CenteredResidualMu"].to_numpy(float)
        raw = group["RawResidualMu"].to_numpy(float)
        binned.append(
            {
                "TransformID": "T2_SN_DISTANCE_MODULUS_RESIDUAL_BINNED",
                "GridIndex": int(idx),
                "z_grid": float(grid[int(idx)]),
                "z_min": float(group["z"].min()),
                "z_max": float(group["z"].max()),
                "Rows": int(len(group)),
                "RawResidualMeanMu": float(np.sum(weights * raw) / denom),
                "CenteredResidualMeanMu": float(np.sum(weights * centered) / denom),
                "SigmaDiagProxy": float(np.sqrt(1.0 / denom)),
                "TransformStatus": "BINNED_SN_PREFLIGHT_NOT_MEASUREMENT_GATE",
                "ClaimBoundary": "preflight_only_same_sample_offset_not_k1_target",
            }
        )
    return pd.DataFrame(binned)
