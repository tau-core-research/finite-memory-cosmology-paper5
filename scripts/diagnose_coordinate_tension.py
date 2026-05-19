#!/usr/bin/env python3
"""Diagnose row-level coordinate tension under operator-only remapping."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized
from fmc.operators import w_k2_locked

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "coordinate_tension_audit.csv"


def bool_series(values: pd.Series) -> np.ndarray:
    """Parse permissive boolean strings from CSV."""
    return values.astype(str).str.lower().isin(["true", "1", "yes", "y"]).to_numpy()


def tension_type(
    inside: bool,
    sign_violation: bool,
    normalized_residual: float,
    k2_value: float,
    lower: float,
    upper: float,
) -> str:
    """Classify row-level tension without changing the model."""
    if sign_violation:
        return "SIGN_STABLE_CONTRADICTION"
    if k2_value > upper:
        return "UPPER_ENVELOPE_EXCESS"
    if k2_value < lower:
        return "LOWER_ENVELOPE_EXCESS"
    if abs(normalized_residual) > 1.0:
        return "DIAGONAL_RESIDUAL_WARNING"
    if not inside:
        return "MAPPING_ONLY_SHIFT"
    return "NON_TENSION"


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)

    z = packet["z"].to_numpy(float)
    x_original = packet["x"].to_numpy(float)
    x_mapped = x_chi_normalized(z)
    k1 = baseline["K1"].to_numpy(float)
    target = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    stable = bool_series(packet["sign_stable"])
    sigma = (upper - lower) / 2.0

    w_original = w_k2_locked(x_original, rho=4.0)
    w_mapped = w_k2_locked(x_mapped, rho=4.0)
    k2_original = k1 * w_original
    k2_mapped = k1 * w_mapped

    rows = []
    for i in range(len(packet)):
        inside = bool(lower[i] <= k2_mapped[i] <= upper[i])
        sign_violation = bool(stable[i] and np.sign(k2_mapped[i]) != np.sign(target[i]))
        normalized_residual = float((target[i] - k2_mapped[i]) / sigma[i])
        rows.append(
            {
                "MappingID": "chi_normalized_flat_lcdm_audit",
                "z": f"{z[i]:.6f}",
                "x_original": f"{x_original[i]:.12g}",
                "x_mapped": f"{x_mapped[i]:.12g}",
                "delta_x": f"{(x_mapped[i] - x_original[i]):.12g}",
                "K1_frozen": f"{k1[i]:.12g}",
                "W_original": f"{w_original[i]:.12g}",
                "W_mapped": f"{w_mapped[i]:.12g}",
                "K2_original": f"{k2_original[i]:.12g}",
                "K2_mapped": f"{k2_mapped[i]:.12g}",
                "target_median": f"{target[i]:.12g}",
                "target_p16": f"{lower[i]:.12g}",
                "target_p84": f"{upper[i]:.12g}",
                "inside_envelope": inside,
                "distance_to_lower": f"{(k2_mapped[i] - lower[i]):.12g}",
                "distance_to_upper": f"{(upper[i] - k2_mapped[i]):.12g}",
                "sign_stable": stable[i],
                "sign_violation": sign_violation,
                "normalized_residual": f"{normalized_residual:.12g}",
                "TensionType": tension_type(
                    inside,
                    sign_violation,
                    normalized_residual,
                    k2_mapped[i],
                    lower[i],
                    upper[i],
                ),
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
