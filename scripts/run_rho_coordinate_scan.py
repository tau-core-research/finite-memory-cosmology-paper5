#!/usr/bin/env python3
"""Scan bounded rho windows for each coordinate mapping."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized, x_index_native, x_optical_depth_like, x_z_normalized
from fmc.gates import classify_gate, envelope_fraction, sign_stable_violations
from fmc.likelihood import chi2, diag_covariance_from_sigma
from fmc.operators import k2_from_k1

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "rho_coordinate_scan.csv"


def bool_series(values: pd.Series) -> np.ndarray:
    """Parse permissive boolean strings from CSV."""
    return values.astype(str).str.lower().isin(["true", "1", "yes", "y"]).to_numpy()


def mapping_set(z: np.ndarray, packet_x: np.ndarray) -> dict[str, np.ndarray]:
    """Return predeclared audit mappings."""
    return {
        "z_normalized_current_packet": packet_x,
        "z_normalized_recomputed": x_z_normalized(z),
        "chi_normalized_flat_lcdm_audit": x_chi_normalized(z),
        "optical_depth_like_uniform": x_optical_depth_like(z),
        "likelihood_native_index": x_index_native(len(z)),
    }


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)

    z = packet["z"].to_numpy(float)
    packet_x = packet["x"].to_numpy(float)
    y = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    stable = bool_series(packet["sign_stable"])
    k1 = baseline["K1"].to_numpy(float)
    sigma = (upper - lower) / 2.0
    covariance = diag_covariance_from_sigma(sigma)

    rho_grid = np.linspace(0.0, 4.0, 41)
    rows = []
    for mapping_name, x_values in mapping_set(z, packet_x).items():
        for rho in rho_grid:
            prediction = k2_from_k1(x_values, k1, rho=float(rho))
            diag_residual = np.abs((y - prediction) / sigma)
            max_abs_residual = float(np.max(diag_residual))
            env = envelope_fraction(prediction, lower, upper)
            violations = sign_stable_violations(prediction, y, stable)
            c2 = chi2(y, prediction, covariance)
            status = classify_gate(
                env,
                violations,
                max_abs_residual=max_abs_residual,
                rho=float(rho),
            )
            rows.append(
                {
                    "MappingID": mapping_name,
                    "rho": f"{rho:.2f}",
                    "p": 3,
                    "Paper5LockedRange": bool(3.0 <= rho <= 4.0),
                    "EnvelopeFraction": f"{env:.10f}",
                    "SignStableViolations": violations,
                    "Chi2DiagProxy": f"{c2:.12g}",
                    "MaxAbsDiagResidual": f"{max_abs_residual:.12g}",
                    "Status": status,
                }
            )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
