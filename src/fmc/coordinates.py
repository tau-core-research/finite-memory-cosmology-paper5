"""Coordinate mappings for finite-memory diagnostic gate checks."""

from __future__ import annotations

import numpy as np


def x_z_normalized(z) -> np.ndarray:
    """Normalize redshift values to the interval endpoint."""
    values = np.asarray(z, dtype=float)
    z_max = float(np.max(values))
    if z_max <= 0.0:
        raise ValueError("z_max must be positive")
    return values / z_max


def x_index_native(n: int) -> np.ndarray:
    """Return a native ordered diagnostic index in [0, 1]."""
    count = int(n)
    if count <= 1:
        raise ValueError("native index mapping requires at least two points")
    return np.linspace(0.0, 1.0, count)


def x_chi_normalized(z, omega_m: float = 0.3, samples: int = 512) -> np.ndarray:
    """Approximate flat-LambdaCDM comoving-distance normalized depth.

    The normalization cancels the common c/H0 factor. This is an audit mapping,
    not a replacement for a full cosmology pipeline.
    """
    values = np.asarray(z, dtype=float)
    if np.any(values < 0.0):
        raise ValueError("redshift values must be non-negative")
    if not 0.0 < float(omega_m) < 1.0:
        raise ValueError("omega_m must be between 0 and 1 for this audit mapping")

    omega_lambda = 1.0 - float(omega_m)

    def integral_to(z_value: float) -> float:
        if z_value == 0.0:
            return 0.0
        grid = np.linspace(0.0, z_value, int(samples))
        e_z = np.sqrt(float(omega_m) * (1.0 + grid) ** 3 + omega_lambda)
        return float(np.trapezoid(1.0 / e_z, grid))

    chi = np.array([integral_to(float(item)) for item in values], dtype=float)
    chi_max = float(np.max(chi))
    if chi_max <= 0.0:
        raise ValueError("chi_max must be positive")
    return chi / chi_max


def x_optical_depth_like(z, weights=None) -> np.ndarray:
    """Return a monotone cumulative visibility/foreground proxy in [0, 1]."""
    values = np.asarray(z, dtype=float)
    order = np.argsort(values)
    if weights is None:
        increments = np.ones_like(values, dtype=float)
    else:
        increments = np.asarray(weights, dtype=float)
        if increments.shape != values.shape:
            raise ValueError("weights must match z shape")
        if np.any(increments < 0.0):
            raise ValueError("weights must be non-negative")

    cumulative_sorted = np.cumsum(increments[order])
    total = float(cumulative_sorted[-1])
    if total <= 0.0:
        raise ValueError("optical-depth-like weights must have positive total")
    mapped = np.empty_like(cumulative_sorted, dtype=float)
    mapped[order] = cumulative_sorted / total
    return mapped
