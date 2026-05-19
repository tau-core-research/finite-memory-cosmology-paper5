"""Null comparator models for finite-memory diagnostic gates."""

from __future__ import annotations

import numpy as np


def null_no_memory(k1):
    """No-memory comparator: use the frozen K1 baseline directly."""
    return np.asarray(k1, dtype=float)


def polynomial_fit(x, y, degree: int):
    """Fixed-degree polynomial comparator fitted to the diagnostic median."""
    coeff = np.polyfit(np.asarray(x, dtype=float), np.asarray(y, dtype=float), int(degree))
    return np.polyval(coeff, np.asarray(x, dtype=float))


def sign_randomized_control(y, seed: int = 0):
    """Sign-randomized control with fixed seed for reproducibility."""
    rng = np.random.default_rng(seed)
    values = np.asarray(y, dtype=float)
    signs = rng.choice([-1.0, 1.0], size=len(values))
    return np.abs(values) * signs


def coordinate_remap_control(x, k1, rho: float = 4.0, alpha: float = 1.2):
    """Monotone coordinate-remap control applied to the memory coordinate."""
    values = np.asarray(x, dtype=float)
    baseline = np.asarray(k1, dtype=float)
    remapped = values**float(alpha)
    return baseline * (1.0 + float(rho) * remapped**3)
