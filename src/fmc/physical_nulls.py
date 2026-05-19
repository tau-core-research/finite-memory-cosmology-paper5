"""Physical-null proxy shapes for source-split preflight contracts.

These helpers define deterministic unit-norm shapes. They do not fit amplitudes
and they do not claim physical validation.
"""

from __future__ import annotations

import numpy as np


def unit_norm(values) -> np.ndarray:
    """Return values scaled to unit Euclidean norm, preserving zero vectors."""
    arr = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(arr))
    if norm <= 0.0:
        return arr
    return arr / norm


def backreaction_broadband_shape(x) -> np.ndarray:
    """Smooth late-depth broadband averaging proxy on a normalized depth grid."""
    values = np.asarray(x, dtype=float)
    raw = values**2 * (1.0 - 0.5 * values)
    raw = raw - float(np.mean(raw))
    return unit_norm(raw)


def dyer_roeder_optical_shape(x) -> np.ndarray:
    """Monotone optical-depth-like propagation proxy on the same depth grid."""
    values = np.asarray(x, dtype=float)
    raw = values * values
    raw = raw - float(np.mean(raw))
    return unit_norm(raw)
