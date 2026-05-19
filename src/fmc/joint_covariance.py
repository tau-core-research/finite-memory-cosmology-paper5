"""Joint source-split covariance helpers.

These utilities build covariance routes for the source-split diagnostic vector.
They are intentionally small and explicit so route choice can be audited.
"""

from __future__ import annotations

import numpy as np


def positive_definite_status(covariance) -> tuple[bool, float, float]:
    """Return positive-definite status and eigenvalue range."""
    cov = np.asarray(covariance, dtype=float)
    eig = np.linalg.eigvalsh(cov)
    return bool(float(np.min(eig)) > 0.0), float(np.min(eig)), float(np.max(eig))


def zero_cross_source_split(sn_covariance, bao_covariance) -> np.ndarray:
    """Source-split covariance with zero SN-BAO cross-covariance."""
    return np.asarray(sn_covariance, dtype=float) + np.asarray(bao_covariance, dtype=float)


def row_aligned_cross_source_split(sn_covariance, bao_covariance, rho_cross: float) -> np.ndarray:
    """Source-split covariance with row-aligned SN-BAO cross-covariance."""
    sn = np.asarray(sn_covariance, dtype=float)
    bao = np.asarray(bao_covariance, dtype=float)
    sn_sigma = np.sqrt(np.maximum(np.diag(sn), 0.0))
    bao_sigma = np.sqrt(np.maximum(np.diag(bao), 0.0))
    cross = np.diag(float(rho_cross) * sn_sigma * bao_sigma)
    return sn + bao - cross - cross.T


def registered_shrinkage(covariance, lambda_shrink: float, x, correlation_length: float) -> np.ndarray:
    """Blend a covariance matrix with a predeclared x-correlation structure."""
    cov = np.asarray(covariance, dtype=float)
    x_values = np.asarray(x, dtype=float)
    sigma = np.sqrt(np.maximum(np.diag(cov), 0.0))
    distance = np.abs(x_values[:, None] - x_values[None, :])
    corr = float(lambda_shrink) * np.exp(-distance / float(correlation_length))
    np.fill_diagonal(corr, 1.0)
    shrink_target = np.outer(sigma, sigma) * corr
    return (1.0 - float(lambda_shrink)) * cov + float(lambda_shrink) * shrink_target
