#!/usr/bin/env python3
"""Build the source-split coordinate map for the likelihood-native K1 route.

This freezes a CMB-parameter comoving-distance coordinate as a preflight map. It
is not marked fully likelihood-native until the joint vector and covariance
policy are promoted together.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.coordinates import x_chi_normalized, x_index_native, x_z_normalized

PARAMS = ROOT / "data" / "k1" / "source_split_likelihood_native_parameters.yaml"
TARGET = ROOT / "data" / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
OUT = ROOT / "data" / "k1" / "source_split_likelihood_native_coordinate_map.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_coordinate_map_summary.csv"


def read_parameters(path: Path) -> dict[str, float]:
    params: dict[str, float] = {}
    in_parameters = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line == "parameters:":
            in_parameters = True
            continue
        if in_parameters and line and not line.startswith(" "):
            break
        if in_parameters and ":" in line:
            key, value = line.strip().split(":", 1)
            try:
                params[key] = float(value.strip())
            except ValueError:
                pass
    return params


def main() -> None:
    params = read_parameters(PARAMS)
    target = pd.read_csv(TARGET)
    z = target["z_grid"].to_numpy(float)
    x_chi = x_chi_normalized(z, omega_m=float(params["OmegaM"]))
    x_z = x_z_normalized(z)
    x_index = x_index_native(len(target))

    output = pd.DataFrame(
        {
            "CoordinateMapID": "SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1",
            "GridIndex": target["GridIndex"].astype(int),
            "z_grid": z,
            "x_likelihood_native": x_chi,
            "x_z_normalized_control": x_z,
            "x_index_control": x_index,
            "CoordinateDefinition": "flat_lcdm_comoving_distance_normalized_with_frozen_cmb_omega_m",
            "OmegaM": float(params["OmegaM"]),
            "Source": "data/k1/source_split_likelihood_native_parameters.yaml",
            "FrozenBeforeK2Scoring": True,
            "LikelihoodNative": False,
            "CoordinateNativePreflight": True,
            "AllowedForK1Export": False,
            "BlockingIssue": "joint_vector_and_covariance_not_promoted",
            "ClaimBoundary": "coordinate_map_preflight_only_no_measurement_validation",
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "LNK1_LIKELIHOOD_NATIVE_COORDINATE_MAP",
                "OutputPath": str(OUT.relative_to(ROOT)),
                "Rows": len(output),
                "CoordinateMapID": "SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1",
                "OmegaM": float(params["OmegaM"]),
                "XMin": float(output["x_likelihood_native"].min()),
                "XMax": float(output["x_likelihood_native"].max()),
                "FrozenBeforeK2Scoring": True,
                "LikelihoodNative": False,
                "AllowedForK1Export": False,
                "BlockingIssue": "joint_vector_and_covariance_not_promoted",
                "NextAction": "Promote joint covariance/nuisance policy before K1 export.",
                "ClaimBoundary": "coordinate_map_preflight_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
