#!/usr/bin/env python3
"""Export the locked K2_SOURCE_SPLIT_A2_PRIOR_V1 prediction vector."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

K1 = DATA / "k1" / "source_split_external_k1_response.csv"


def target_regime(x: float) -> str:
    if x < 0.5:
        return "low_depth_baseline_dominated"
    if x < 0.8:
        return "mid_depth_memory_transition"
    return "high_depth_memory_active"


def main() -> None:
    k1 = pd.read_csv(K1).copy()
    k1["K2UnitLockedRho4"] = k1["K1Response"] * (1.0 + 4.0 * k1["x_coordinate"] ** 3)
    k1["A_tau"] = 2.0
    k1["K2SourceSplitA2Prediction"] = k1["A_tau"] * k1["K2UnitLockedRho4"]
    k1["PredictionID"] = "K2_SOURCE_SPLIT_A2_PRIOR_V1"
    k1["TargetRegime"] = [target_regime(float(x)) for x in k1["x_coordinate"]]
    k1["PredictionStatus"] = "LOCKED_PREDICTION_CANDIDATE"
    k1["KernelChanged"] = False
    k1["Rho"] = 4.0
    k1["P"] = 3
    k1["FittedInThisNote"] = False
    k1["ClaimBoundary"] = "locked_prediction_candidate_no_measurement_validation"

    cols = [
        "PredictionID",
        "GridIndex",
        "z_grid",
        "x_coordinate",
        "x_mapping",
        "K1Response",
        "K2UnitLockedRho4",
        "A_tau",
        "K2SourceSplitA2Prediction",
        "TargetRegime",
        "PredictionStatus",
        "KernelChanged",
        "Rho",
        "P",
        "FittedInThisNote",
        "ClaimBoundary",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    k1[cols].to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
