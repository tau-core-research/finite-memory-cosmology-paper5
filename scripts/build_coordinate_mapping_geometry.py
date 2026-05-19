#!/usr/bin/env python3
"""Build geometry table for coordinate mappings used in audit runs."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized, x_index_native, x_optical_depth_like, x_z_normalized
from fmc.operators import w_k2_locked

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
OUT = ROOT / "evidence" / "coordinate_mapping_geometry.csv"


def main() -> None:
    packet = pd.read_csv(PACKET)
    z = packet["z"].to_numpy(float)
    x_z = x_z_normalized(z)
    x_chi = x_chi_normalized(z)
    x_optical = x_optical_depth_like(z)
    x_native = x_index_native(len(z))
    w_z = w_k2_locked(x_z, rho=4.0)
    w_chi = w_k2_locked(x_chi, rho=4.0)

    rows = []
    for i in range(len(packet)):
        rows.append(
            {
                "z": f"{z[i]:.6f}",
                "x_z_normalized": f"{x_z[i]:.12g}",
                "x_chi_normalized": f"{x_chi[i]:.12g}",
                "x_optical_depth_like": f"{x_optical[i]:.12g}",
                "x_likelihood_native": f"{x_native[i]:.12g}",
                "delta_chi_minus_z": f"{(x_chi[i] - x_z[i]):.12g}",
                "W_z": f"{w_z[i]:.12g}",
                "W_chi": f"{w_chi[i]:.12g}",
                "W_ratio_chi_to_z": f"{(w_chi[i] / w_z[i]):.12g}",
            }
        )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
