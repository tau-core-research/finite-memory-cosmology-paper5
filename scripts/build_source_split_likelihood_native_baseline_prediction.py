#!/usr/bin/env python3
"""Build a preflight baseline prediction vector for likelihood-native K1.

This exports the next artifact in the source-split likelihood-native route. It
uses the frozen CMB-only parameter source, but it does not promote the result to
primary K1 because SN nuisance handling and the likelihood-native coordinate map
are still not frozen.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.bao_transform import bao_log_residual_transform
from fmc.public_data import (
    load_bao_mean,
    load_flat_covariance_with_size,
    load_pantheon_table,
    load_square_covariance,
)
from fmc.sn_transform import bin_sn_residuals_to_grid, sn_residual_transform

PARAMS = ROOT / "data" / "k1" / "source_split_likelihood_native_parameters.yaml"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
PANTHEON = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES.dat"
PANTHEON_COV = ROOT / "data" / "public_ingest" / "pantheon_plus" / "Pantheon_SH0ES_STAT_SYS.cov"
BAO_MEAN = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_mean.txt"
BAO_COV = ROOT / "data" / "public_ingest" / "desi_dr2" / "desi_gaussian_bao_ALL_GCcomb_cov.txt"

OUT = ROOT / "data" / "k1" / "source_split_likelihood_native_baseline_prediction.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_baseline_prediction_summary.csv"
COORDINATE_MAP = ROOT / "data" / "k1" / "source_split_likelihood_native_coordinate_map.csv"


def read_simple_yaml(path: Path) -> dict[str, object]:
    """Read the simple YAML emitted by build_source_split_likelihood_native_parameters.py."""
    result: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1]
            result[current_key] = {}
            continue
        if not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key] = parse_scalar(value.strip())
            current_key = None
            continue
        if current_key and ":" in line:
            key, value = line.strip().split(":", 1)
            assert isinstance(result[current_key], dict)
            result[current_key][key] = parse_scalar(value.strip())
    return result


def parse_scalar(value: str) -> object:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return float(value)
    except ValueError:
        return value


def weighted_mean(values: np.ndarray, sigma: np.ndarray) -> tuple[float, float]:
    weights = np.where(sigma > 0.0, 1.0 / (sigma * sigma), 0.0)
    denom = float(np.sum(weights))
    if denom <= 0.0:
        return float("nan"), float("nan")
    return float(np.sum(weights * values) / denom), float(np.sqrt(1.0 / denom))


def nearest_bao_anchor(bao: pd.DataFrame, z: float) -> dict[str, object]:
    distances = np.abs(bao["z"].to_numpy(float) - float(z))
    nearest_distance = float(np.min(distances))
    group = bao[distances == nearest_distance]
    raw_mean, sigma = weighted_mean(group["LogResidual"].to_numpy(float), group["SigmaDiag"].to_numpy(float))
    return {
        "BAONearestZ": float(group["z"].iloc[0]),
        "BAOAnchorRows": int(len(group)),
        "BAOBaselineLogResidual": raw_mean,
        "BAOSigmaDiagProxy": sigma,
        "BAOAnchorDeltaZ": nearest_distance,
        "BAOQuantities": "|".join(sorted(set(group["Quantity"].astype(str)))),
    }


def main() -> None:
    params_doc = read_simple_yaml(PARAMS)
    params = params_doc["parameters"]
    assert isinstance(params, dict)
    baseline = {
        "baseline_id": str(params_doc["baseline_id"]),
        "H0": float(params["H0"]),
        "omega_m": float(params["OmegaM"]),
        "rd_mpc": float(params["rd_mpc"]),
    }

    target = pd.read_csv(TARGET)
    target = target[target["HasSNAndBAO"].astype(bool)].copy()
    coordinate_issue = (
        "coordinate_map_preflight_not_promoted" if COORDINATE_MAP.exists() else "coordinate_map_missing"
    )
    blocking_issue = f"sn_nuisance_not_likelihood_native;{coordinate_issue};joint_covariance_not_promoted"

    sn_table = load_pantheon_table(PANTHEON)
    sn_cov = load_flat_covariance_with_size(PANTHEON_COV)
    sn_rows = sn_residual_transform(sn_table, sn_cov, "PANTHEON_PLUS_SH0ES_SN", baseline=baseline)
    sn_bins = bin_sn_residuals_to_grid(sn_rows, target["z_grid"].to_numpy(float))

    bao_mean = load_bao_mean(BAO_MEAN)
    bao_cov = load_square_covariance(BAO_COV)
    bao_rows, _ = bao_log_residual_transform(bao_mean, bao_cov, "DESI_DR2_BAO_ALL_GAUSSIAN", baseline=baseline)

    rows: list[dict[str, object]] = []
    for _, item in target.iterrows():
        grid_index = int(item["GridIndex"])
        z = float(item["z_grid"])
        sn_match = sn_bins[sn_bins["z_grid"].round(10).eq(round(z, 10))]
        if sn_match.empty:
            continue
        sn = sn_match.iloc[0]
        bao = nearest_bao_anchor(bao_rows, z)
        sn_raw = float(sn["RawResidualMeanMu"])
        sn_centered = float(sn["CenteredResidualMeanMu"])
        sn_sigma = float(sn["SigmaDiagProxy"])
        bao_resid = float(bao["BAOBaselineLogResidual"])
        bao_sigma = float(bao["BAOSigmaDiagProxy"])
        joint_sigma = float(np.sqrt(sn_sigma * sn_sigma + bao_sigma * bao_sigma))
        rows.append(
            {
                "BaselineVectorID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_BASELINE_PREDICTION_PREFLIGHT_V1",
                "BaselineID": baseline["baseline_id"],
                "GridIndex": grid_index,
                "z_grid": z,
                "x_coordinate_preflight": float(item["x_coordinate"]),
                "x_mapping_preflight": item["x_mapping"],
                "SNRawResidualMu": sn_raw,
                "SNSameSampleCenteredResidualMu": sn_centered,
                "SNSigmaDiagProxy": sn_sigma,
                "BAOBaselineLogResidual": bao_resid,
                "BAOSigmaDiagProxy": bao_sigma,
                "BAONearestZ": bao["BAONearestZ"],
                "BAOAnchorDeltaZ": bao["BAOAnchorDeltaZ"],
                "BAOQuantities": bao["BAOQuantities"],
                "RawSourceSplitResponse": sn_raw - bao_resid,
                "CenteredControlSourceSplitResponse": sn_centered - bao_resid,
                "JointSigmaDiagProxy": joint_sigma,
                "LikelihoodNative": False,
                "CoordinateNative": False,
                "AllowedAsPrimaryK1Candidate": False,
                "BlockingIssue": blocking_issue,
                "ClaimBoundary": "baseline_prediction_preflight_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "LNK1_BASELINE_PREDICTION_VECTOR",
                "OutputPath": str(OUT.relative_to(ROOT)),
                "Rows": len(output),
                "BaselineID": baseline["baseline_id"],
                "MeanAbsRawSourceSplitResponse": float(output["RawSourceSplitResponse"].abs().mean()),
                "MeanAbsCenteredControlSourceSplitResponse": float(
                    output["CenteredControlSourceSplitResponse"].abs().mean()
                ),
                "MeanJointSigmaDiagProxy": float(output["JointSigmaDiagProxy"].mean()),
                "AllowedAsPrimaryK1Candidate": False,
                "BlockingIssue": blocking_issue,
                "NextAction": "Freeze likelihood-native coordinate map and nuisance/covariance policy before K1 export.",
                "ClaimBoundary": "baseline_prediction_preflight_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
