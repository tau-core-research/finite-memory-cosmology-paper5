"""Locked finite-memory operators and audit utilities."""

from __future__ import annotations

import numpy as np


def w_power(x, rho: float, p: int) -> np.ndarray:
    """Return W_p(x) = 1 + rho*x^p."""
    values = np.asarray(x, dtype=float)
    return 1.0 + float(rho) * values**int(p)


def w_k2_locked(x, rho: float = 4.0) -> np.ndarray:
    """Return the current locked cubic K2 memory factor."""
    return w_power(x, rho=rho, p=3)


def k2_from_k1(x, k1, rho: float = 4.0) -> np.ndarray:
    """Apply the locked K2 finite-memory multiplier to a frozen K1 baseline."""
    return w_k2_locked(x, rho=rho) * np.asarray(k1, dtype=float)


def passive_bound_ok(rho: float, p: int = 3) -> bool:
    """Check the passive memory budget rho <= p + 1."""
    return float(rho) <= int(p) + 1


def low_depth_visibility(p: int, x0: float = 0.25) -> float:
    """Visibility of the saturated power kernel at low depth."""
    return float((int(p) + 1) * float(x0) ** int(p))


def endpoint_budget(p: int, x0: float = 0.75) -> float:
    """Fraction of saturated power-kernel memory budget in the endpoint tail."""
    return float(1.0 - float(x0) ** (int(p) + 1))

