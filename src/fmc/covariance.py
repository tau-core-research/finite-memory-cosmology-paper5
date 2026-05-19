"""Covariance proxy builders and public-covariance placeholders."""

from __future__ import annotations

import numpy as np


def covariance_from_correlation(sigma, corr) -> np.ndarray:
    """Build covariance from pointwise sigma and a correlation matrix."""
    values = np.asarray(sigma, dtype=float)
    return np.outer(values, values) * np.asarray(corr, dtype=float)


def diagonal(sigma) -> np.ndarray:
    """Diagonal covariance proxy."""
    values = np.asarray(sigma, dtype=float)
    return np.diag(values**2)


def nearest_neighbor(sigma, rho_corr: float = 0.25) -> np.ndarray:
    """Nearest-neighbor correlation covariance proxy."""
    values = np.asarray(sigma, dtype=float)
    corr = np.eye(len(values))
    for i in range(len(values) - 1):
        corr[i, i + 1] = corr[i + 1, i] = float(rho_corr)
    return covariance_from_correlation(values, corr)


def exponential_in_z(sigma, z) -> np.ndarray:
    """Exponential correlation proxy in redshift coordinate."""
    z_values = np.asarray(z, dtype=float)
    scale = max(float(np.ptp(z_values)) / 3.0, 1e-6)
    corr = np.exp(-np.abs(z_values[:, None] - z_values[None, :]) / scale)
    return covariance_from_correlation(sigma, corr)


def exponential_in_x(sigma, x) -> np.ndarray:
    """Exponential correlation proxy in diagnostic coordinate."""
    x_values = np.asarray(x, dtype=float)
    scale = max(float(np.ptp(x_values)) / 3.0, 1e-6)
    corr = np.exp(-np.abs(x_values[:, None] - x_values[None, :]) / scale)
    return covariance_from_correlation(sigma, corr)


def constant_offdiagonal(sigma, rho_corr: float = 0.15) -> np.ndarray:
    """Constant off-diagonal correlation covariance proxy."""
    values = np.asarray(sigma, dtype=float)
    corr = np.full((len(values), len(values)), float(rho_corr))
    np.fill_diagonal(corr, 1.0)
    return covariance_from_correlation(values, corr)


def public_full_covariance_placeholder(*_args, **_kwargs) -> np.ndarray:
    """Placeholder for future public full covariance ingestion."""
    raise NotImplementedError("public full covariance ingestion is a Phase II requirement")
