#!/usr/bin/env python3
"""Diagnose amplitude mismatch for likelihood-native K1/K2 preflight scoring."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fmc.operators import w_k2_locked

EXTERNAL_K1 = ROOT / "data" / "k1" / "source_split_external_k1_response.csv"
TARGET = ROOT / "evidence" / "source_split_coordinate_native_target.csv"
OUT = ROOT / "evidence" / "source_split_likelihood_native_amplitude_gap_audit.csv"
SUMMARY = ROOT / "evidence" / "source_split_likelihood_native_amplitude_gap_summary.csv"


def main() -> None:
    external = pd.read_csv(EXTERNAL_K1)
    target = pd.read_csv(TARGET)
    data = external.merge(
        target[["GridIndex", "SourceSplitResponse", "SignStableTemplate"]],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    x = data["x_coordinate"].to_numpy(float)
    target_response = data["SourceSplitResponse"].to_numpy(float)
    k1 = data["K1Response"].to_numpy(float)
    k2 = w_k2_locked(x, rho=4.0) * k1
    sigma = data["K1Sigma"].to_numpy(float)

    def safe_ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
        return np.where(np.abs(den) > 1e-12, num / den, np.nan)

    rows = pd.DataFrame(
        {
            "GridIndex": data["GridIndex"].astype(int),
            "z_grid": data["z_grid"].astype(float),
            "x_coordinate": x,
            "TargetResponse": target_response,
            "K1Response": k1,
            "K2Rho4Response": k2,
            "SigmaDiag": sigma,
            "AbsTarget": np.abs(target_response),
            "AbsK1": np.abs(k1),
            "AbsK2Rho4": np.abs(k2),
            "TargetOverK1": safe_ratio(target_response, k1),
            "TargetOverK2Rho4": safe_ratio(target_response, k2),
            "K2OverK1": safe_ratio(k2, k1),
            "K1ResidualOverSigma": (target_response - k1) / sigma,
            "K2ResidualOverSigma": (target_response - k2) / sigma,
            "DominanceNote": np.where(
                np.abs(target_response) > 5.0 * np.maximum(np.abs(k2), 1e-12),
                "target_amplitude_exceeds_k2_by_gt_5x",
                "amplitude_gap_moderate_or_small",
            ),
            "ClaimBoundary": "amplitude_gap_diagnosis_only_no_measurement_validation",
        }
    )
    rows.to_csv(OUT, index=False)

    low_depth = rows[rows["x_coordinate"] <= 0.5]
    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_LIKELIHOOD_NATIVE_AMPLITUDE_GAP",
                "Rows": len(rows),
                "RowsTargetGt5xK2": int(rows["DominanceNote"].eq("target_amplitude_exceeds_k2_by_gt_5x").sum()),
                "MeanAbsTarget": float(rows["AbsTarget"].mean()),
                "MeanAbsK1": float(rows["AbsK1"].mean()),
                "MeanAbsK2Rho4": float(rows["AbsK2Rho4"].mean()),
                "LowDepthRows": len(low_depth),
                "LowDepthMeanAbsTarget": float(low_depth["AbsTarget"].mean()) if not low_depth.empty else np.nan,
                "LowDepthMeanAbsK2Rho4": float(low_depth["AbsK2Rho4"].mean()) if not low_depth.empty else np.nan,
                "Interpretation": "k2_shape_improves_k1_but_amplitude_gap_dominates_low_depth_rows",
                "NextAction": "Do not rescale K1 post hoc; evaluate whether likelihood-native target scale or covariance proxy is appropriate.",
                "ClaimBoundary": "amplitude_gap_diagnosis_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
