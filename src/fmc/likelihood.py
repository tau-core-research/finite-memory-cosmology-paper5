"""Small likelihood and score utilities for diagnostic gate runs."""

from __future__ import annotations

import numpy as np


def chi2(y, model, covariance) -> float:
    """Return r^T C^-1 r for a diagnostic vector."""
    residual = np.asarray(y, dtype=float) - np.asarray(model, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    return float(residual.T @ np.linalg.solve(cov, residual))


def diag_covariance_from_sigma(sigma) -> np.ndarray:
    """Build a diagonal covariance proxy from pointwise sigma values."""
    sigma_values = np.asarray(sigma, dtype=float)
    return np.diag(sigma_values**2)


def shrink_covariance(covariance, lam: float = 0.1) -> np.ndarray:
    """Shrink a covariance matrix toward its diagonal."""
    cov = np.asarray(covariance, dtype=float)
    diagonal = np.diag(np.diag(cov))
    return (1.0 - float(lam)) * cov + float(lam) * diagonal


def aic(chi2_value: float, k: int) -> float:
    """Akaike information criterion for a fixed diagnostic score."""
    return float(chi2_value) + 2 * int(k)


def bic(chi2_value: float, k: int, n: int) -> float:
    """Bayesian information criterion for a fixed diagnostic score."""
    return float(chi2_value) + int(k) * float(np.log(int(n)))

