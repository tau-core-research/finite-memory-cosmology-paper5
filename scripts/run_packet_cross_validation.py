#!/usr/bin/env python3
"""Run simple current-packet cross-validation diagnostics."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.benchmark import bool_series, mapping_set
from fmc.operators import k2_from_k1

PACKET = ROOT / "evidence" / "diagnostic_point_audit.csv"
BASELINE = ROOT / "frozen" / "k1_baseline_v1.csv"
OUT = ROOT / "evidence" / "cross_validation_results.csv"


def weighted_mse(y, pred, sigma) -> float:
    residual = (np.asarray(y, dtype=float) - np.asarray(pred, dtype=float)) / np.asarray(sigma, dtype=float)
    return float(np.mean(residual**2))


def fit_poly_predict(x_train, y_train, x_test, degree: int):
    coeff = np.polyfit(x_train, y_train, degree)
    return np.polyval(coeff, x_test)


def main() -> None:
    packet = pd.read_csv(PACKET)
    baseline = pd.read_csv(BASELINE)
    z = packet["z"].to_numpy(float)
    packet_x = packet["x"].to_numpy(float)
    y = packet["target_median"].to_numpy(float)
    lower = packet["target_p16"].to_numpy(float)
    upper = packet["target_p84"].to_numpy(float)
    sigma = (upper - lower) / 2.0
    stable = bool_series(packet["sign_stable"])
    k1 = baseline["K1"].to_numpy(float)

    rows = []
    for mapping_id, x_values in mapping_set(z, packet_x).items():
        k2_pred = k2_from_k1(x_values, k1, rho=4.0)
        k1_pred = k1
        for i in range(len(y)):
            train = np.ones(len(y), dtype=bool)
            train[i] = False
            test = ~train
            for model_id, pred, k in [
                ("K2_LOCKED_RHO4", k2_pred[test], 0),
                ("K1_NO_MEMORY", k1_pred[test], 0),
                ("POLY_DEG2", fit_poly_predict(x_values[train], y[train], x_values[test], 2), 3),
                ("POLY_DEG3", fit_poly_predict(x_values[train], y[train], x_values[test], 3), 4),
            ]:
                rows.append(
                    {
                        "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                        "Mapping": mapping_id,
                        "ValidationMode": "leave_one_out",
                        "Fold": f"z_{z[i]:.6f}",
                        "Model": model_id,
                        "ParameterCount": k,
                        "TestN": 1,
                        "WeightedMSE": f"{weighted_mse(y[test], pred, sigma[test]):.12g}",
                    }
                )
        blocks = {
            "low_depth_block": x_values <= 1 / 3,
            "mid_depth_block": (x_values > 1 / 3) & (x_values <= 2 / 3),
            "high_depth_block": x_values > 2 / 3,
            "sign_stable_block": stable,
            "sign_unstable_block": ~stable,
        }
        for block_id, test in blocks.items():
            if int(test.sum()) < 1 or int((~test).sum()) < 4:
                continue
            train = ~test
            for model_id, pred, k in [
                ("K2_LOCKED_RHO4", k2_pred[test], 0),
                ("K1_NO_MEMORY", k1_pred[test], 0),
                ("POLY_DEG2", fit_poly_predict(x_values[train], y[train], x_values[test], 2), 3),
                ("POLY_DEG3", fit_poly_predict(x_values[train], y[train], x_values[test], 3), 4),
            ]:
                rows.append(
                    {
                        "Dataset": "SN_BAO_NO_DEGREE4_CURRENT",
                        "Mapping": mapping_id,
                        "ValidationMode": "blocked_split",
                        "Fold": block_id,
                        "Model": model_id,
                        "ParameterCount": k,
                        "TestN": int(test.sum()),
                        "WeightedMSE": f"{weighted_mse(y[test], pred, sigma[test]):.12g}",
                    }
                )

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
