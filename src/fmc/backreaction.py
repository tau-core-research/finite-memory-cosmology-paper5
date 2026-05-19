"""Backreaction formula utilities.

These helpers implement the formula route only. They do not calibrate a
backreaction null by themselves because the source-native reconstruction vector
and covariance must be supplied externally.
"""

from __future__ import annotations

import numpy as np


REQUIRED_RECONSTRUCTION_COLUMNS = [
    "z",
    "D",
    "D_prime",
    "D_double_prime",
    "H_D",
    "H_D_prime",
]

RECONSTRUCTION_COVARIANCE_COLUMNS = [
    "D",
    "D_prime",
    "D_double_prime",
    "H_D",
    "H_D_prime",
]


def omega_r_plus_3omega_q(z, D, D_prime, D_double_prime, H_D, H_D_prime) -> np.ndarray:
    """Compute Omega_R + 3 Omega_Q from the Koksbang addendum formula.

    Formula:
        ((1 + z)^2 / D) * ((H_D_prime * D_prime / H_D) + D_double_prime)

    The caller is responsible for using a source-native reconstruction of D,
    H_D and derivatives. This function intentionally performs no fitting,
    smoothing, figure digitization, or covariance construction.
    """
    z_arr = np.asarray(z, dtype=float)
    D_arr = np.asarray(D, dtype=float)
    Dp_arr = np.asarray(D_prime, dtype=float)
    Dpp_arr = np.asarray(D_double_prime, dtype=float)
    H_arr = np.asarray(H_D, dtype=float)
    Hp_arr = np.asarray(H_D_prime, dtype=float)

    if np.any(D_arr == 0.0):
        raise ValueError("D contains zero values; backreaction formula would divide by zero")
    if np.any(H_arr == 0.0):
        raise ValueError("H_D contains zero values; backreaction formula would divide by zero")

    return ((1.0 + z_arr) ** 2 / D_arr) * ((Hp_arr * Dp_arr / H_arr) + Dpp_arr)


def omega_formula_jacobian(z, D, D_prime, D_double_prime, H_D, H_D_prime) -> np.ndarray:
    """Return row-wise Jacobian for the backreaction formula.

    The returned matrix has shape ``(N, 5N)`` and assumes the source-native input
    covariance is ordered row-wise as ``D, D_prime, D_double_prime, H_D,
    H_D_prime`` for each redshift row. Redshift is treated as the fixed grid.
    """
    z_arr = np.asarray(z, dtype=float)
    D_arr = np.asarray(D, dtype=float)
    Dp_arr = np.asarray(D_prime, dtype=float)
    Dpp_arr = np.asarray(D_double_prime, dtype=float)
    H_arr = np.asarray(H_D, dtype=float)
    Hp_arr = np.asarray(H_D_prime, dtype=float)

    if np.any(D_arr == 0.0):
        raise ValueError("D contains zero values; backreaction formula would divide by zero")
    if np.any(H_arr == 0.0):
        raise ValueError("H_D contains zero values; backreaction formula would divide by zero")

    n = len(z_arr)
    jac = np.zeros((n, 5 * n), dtype=float)
    pref = (1.0 + z_arr) ** 2
    bracket = (Hp_arr * Dp_arr / H_arr) + Dpp_arr

    for i in range(n):
        base = 5 * i
        jac[i, base + 0] = -pref[i] * bracket[i] / (D_arr[i] ** 2)
        jac[i, base + 1] = pref[i] * Hp_arr[i] / (D_arr[i] * H_arr[i])
        jac[i, base + 2] = pref[i] / D_arr[i]
        jac[i, base + 3] = -pref[i] * Hp_arr[i] * Dp_arr[i] / (D_arr[i] * H_arr[i] ** 2)
        jac[i, base + 4] = pref[i] * Dp_arr[i] / (D_arr[i] * H_arr[i])
    return jac


def propagate_omega_covariance(input_covariance, z, D, D_prime, D_double_prime, H_D, H_D_prime) -> np.ndarray:
    """Propagate source-native reconstruction covariance through the formula."""
    cov = np.asarray(input_covariance, dtype=float)
    jac = omega_formula_jacobian(z, D, D_prime, D_double_prime, H_D, H_D_prime)
    expected = jac.shape[1]
    if cov.shape != (expected, expected):
        raise ValueError(f"input covariance shape must be {(expected, expected)}, got {cov.shape}")
    return jac @ cov @ jac.T


def validate_reconstruction_columns(columns) -> list[str]:
    """Return missing required reconstruction columns."""
    available = {str(col) for col in columns}
    return [col for col in REQUIRED_RECONSTRUCTION_COLUMNS if col not in available]
