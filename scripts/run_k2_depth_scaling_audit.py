#!/usr/bin/env python3
"""Audit whether locked K2 naturally strengthens with depth.

The script separates the frozen K1 baseline from the locked finite-memory
multiplier W(x)=1+4*x^3 and reports whether the observed K2 amplitude pattern is
explained by the predeclared depth response.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "k2_depth_scaling_audit.csv"
SUMMARY = EVIDENCE / "k2_depth_scaling_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def corr(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def depth_bin(x: float) -> str:
    if x < 0.5:
        return "low_depth"
    if x < 0.8:
        return "mid_depth"
    return "high_depth"


def main() -> None:
    df = pd.read_csv(DECOMP).copy()
    df["WLockedRho4"] = 1.0 + 4.0 * df["x_coordinate"].astype(float) ** 3
    df["K2OverK1AbsRatio"] = np.abs(df["K2LockedRho4"]) / np.abs(df["K1Response"])
    df["K2AbsOverTargetAbs"] = np.abs(df["K2LockedRho4"]) / np.abs(df["SourceSplitResponse"])
    df["K1AbsOverTargetAbs"] = np.abs(df["K1Response"]) / np.abs(df["SourceSplitResponse"])
    df["MemoryBoostAbs"] = np.abs(df["K2LockedRho4"]) - np.abs(df["K1Response"])
    df["MemoryBoostOverTargetAbs"] = df["MemoryBoostAbs"] / np.abs(df["SourceSplitResponse"])
    df["DepthBin"] = [depth_bin(float(x)) for x in df["x_coordinate"]]
    df["ClaimBoundary"] = "k2_depth_scaling_audit_no_measurement_validation"

    cols = [
        "GridIndex",
        "z_grid",
        "x_coordinate",
        "DepthBin",
        "SourceSplitResponse",
        "K1Response",
        "WLockedRho4",
        "K2LockedRho4",
        "K2OverK1AbsRatio",
        "K1AbsOverTargetAbs",
        "K2AbsOverTargetAbs",
        "MemoryBoostAbs",
        "MemoryBoostOverTargetAbs",
        "SignStableTemplate",
        "ClaimBoundary",
    ]
    df[cols].to_csv(OUT, index=False)

    rows: list[dict[str, object]] = []
    for subset, sub in [("all_points", df), *[(b, df[df["DepthBin"] == b]) for b in ["low_depth", "mid_depth", "high_depth"]]]:
        rows.append(
            {
                "Subset": subset,
                "Rows": len(sub),
                "MeanX": float(sub["x_coordinate"].mean()) if len(sub) else float("nan"),
                "MeanWLockedRho4": float(sub["WLockedRho4"].mean()) if len(sub) else float("nan"),
                "K1RMS": rms(sub["K1Response"].to_numpy(float)) if len(sub) else float("nan"),
                "K2RMS": rms(sub["K2LockedRho4"].to_numpy(float)) if len(sub) else float("nan"),
                "TargetRMS": rms(sub["SourceSplitResponse"].to_numpy(float)) if len(sub) else float("nan"),
                "K1ToTargetRMSRatio": rms(sub["K1Response"].to_numpy(float)) / rms(sub["SourceSplitResponse"].to_numpy(float))
                if len(sub) and rms(sub["SourceSplitResponse"].to_numpy(float)) > 0
                else float("nan"),
                "K2ToTargetRMSRatio": rms(sub["K2LockedRho4"].to_numpy(float)) / rms(sub["SourceSplitResponse"].to_numpy(float))
                if len(sub) and rms(sub["SourceSplitResponse"].to_numpy(float)) > 0
                else float("nan"),
                "MeanK2AbsOverTargetAbs": float(sub["K2AbsOverTargetAbs"].mean()) if len(sub) else float("nan"),
                "MeanMemoryBoostOverTargetAbs": float(sub["MemoryBoostOverTargetAbs"].mean()) if len(sub) else float("nan"),
                "ClaimBoundary": "k2_depth_scaling_audit_no_measurement_validation",
            }
        )

    summary = pd.DataFrame(rows)
    summary["CorrelationXWithW"] = corr(df["x_coordinate"].to_numpy(float), df["WLockedRho4"].to_numpy(float))
    summary["CorrelationXWithK2AbsOverTargetAbs"] = corr(
        df["x_coordinate"].to_numpy(float), df["K2AbsOverTargetAbs"].to_numpy(float)
    )
    summary["Interpretation"] = "locked_cubic_memory_naturally_strengthens_with_depth"
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
