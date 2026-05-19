"""Diagnostic gate classification helpers."""

from __future__ import annotations

import numpy as np


def envelope_fraction(prediction, lower, upper) -> float:
    """Fraction of model points inside the diagnostic envelope."""
    pred = np.asarray(prediction, dtype=float)
    lo = np.asarray(lower, dtype=float)
    hi = np.asarray(upper, dtype=float)
    return float(np.mean((pred >= lo) & (pred <= hi)))


def sign_stable_violations(prediction, target, sign_stable) -> int:
    """Count sign mismatches only where the target sign is reconstruction-stable."""
    pred = np.asarray(prediction, dtype=float)
    y = np.asarray(target, dtype=float)
    stable = np.asarray(sign_stable, dtype=bool)
    return int(np.sum(np.sign(pred[stable]) != np.sign(y[stable])))


def classify_gate(
    envelope_frac: float,
    sign_violations: int,
    max_abs_residual: float | None = None,
    residual_limit: float = 1.0,
    rho: float | None = None,
    rho_bound: float = 4.0,
) -> str:
    """Classify a diagnostic gate result without promoting it to validation."""
    if rho is not None and float(rho) > float(rho_bound):
        return "RHO_BOUND_EXCEEDED"
    if int(sign_violations) > 0:
        return "STRICT_GATE_WARNING"
    if max_abs_residual is not None and float(max_abs_residual) <= float(residual_limit):
        return "NON_VIOLATING_DIAGNOSTIC"
    if float(envelope_frac) < 1.0:
        return "ENVELOPE_TENSION"
    return "NON_VIOLATING_DIAGNOSTIC"
