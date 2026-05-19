#!/usr/bin/env python3
"""Run simple covariance-proxy sensitivity checks for the current packet."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.benchmark import mapping_set, model_predictions
from fmc.covariance import constant_offdiagonal, diagonal, exponential_in_x, exponential_in_z, nearest_neighbor
from fmc.likelihood import aic, bic, chi2

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "shrinkage_covariance_sensitivity.csv"


def covariance_proxy(kind: str, sigma, z, x):
    """Build one named covariance proxy."""
    if kind == "diagonal":
        return diagonal(sigma)
    if kind == "nearest_neighbor_corr":
        return nearest_neighbor(sigma)
    if kind == "exp_corr_z":
        return exponential_in_z(sigma, z)
    if kind == "exp_corr_x":
        return exponential_in_x(sigma, x)
    if kind == "constant_offdiag_corr":
        return constant_offdiagonal(sigma)
    raise ValueError(f"unknown covariance proxy {kind}")


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)
    z = packet["z"].to_numpy(float)
    packet_x = packet["x"].to_numpy(float)
    y = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    sigma = (upper - lower) / 2.0
    k1 = baseline["K1"].to_numpy(float)

    rows = []
    for mapping_id, x_values in mapping_set(z, packet_x).items():
        for cov_id in ["diagonal", "nearest_neighbor_corr", "exp_corr_z", "exp_corr_x", "constant_offdiag_corr"]:
            cov = covariance_proxy(cov_id, sigma, z, x_values)
            for model in model_predictions(x_values, k1, y):
                k = int(model["ParameterCount"])
                c2 = chi2(y, model["Prediction"], cov)
                rows.append(
                    {
                        "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                        "Mapping": mapping_id,
                        "CovarianceProxy": cov_id,
                        "Model": model["Model"],
                        "ParameterCount": k,
                        "Chi2Proxy": f"{c2:.12g}",
                        "AIC": f"{aic(c2, k):.12g}",
                        "BIC": f"{bic(c2, k, len(y)):.12g}",
                    }
                )

    df = pd.DataFrame(rows)
    df["DeltaAIC_vs_K2"] = ""
    df["DeltaBIC_vs_K2"] = ""
    for (mapping_id, cov_id), idx in df.groupby(["Mapping", "CovarianceProxy"]).groups.items():
        group = df.loc[idx]
        ref = group[group["Model"] == "K2_LOCKED_RHO4"].iloc[0]
        df.loc[idx, "DeltaAIC_vs_K2"] = group["AIC"].astype(float) - float(ref["AIC"])
        df.loc[idx, "DeltaBIC_vs_K2"] = group["BIC"].astype(float) - float(ref["BIC"])
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
