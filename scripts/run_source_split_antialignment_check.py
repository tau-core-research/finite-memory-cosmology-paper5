#!/usr/bin/env python3
"""Check SN/BAO anti-alignment behind the A_tau=2 source-split prior."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DECOMP = EVIDENCE / "k2_residual_decomposition.csv"
OUT = EVIDENCE / "source_split_antialignment_check.csv"
SUMMARY = EVIDENCE / "source_split_antialignment_summary.csv"


def sign(value: float) -> int:
    if not math.isfinite(value) or abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def summarize(df: pd.DataFrame, subset: str) -> dict[str, object]:
    if df.empty:
        return {
            "Subset": subset,
            "Rows": 0,
            "OppositeSignFraction": float("nan"),
            "K2MatchesSourceSplitFraction": float("nan"),
            "AntiAlignedAndK2MatchedFraction": float("nan"),
            "MeanAbsSN": float("nan"),
            "MeanAbsBAO": float("nan"),
            "MeanSignedChannelProduct": float("nan"),
            "SupportsATau2Prior": False,
            "ClaimBoundary": "source_split_antialignment_preflight_no_measurement_validation",
        }

    opposite = df["SNBAOOppositeSign"].astype(bool).to_numpy()
    k2match = df["K2MatchesSourceSplitSign"].astype(bool).to_numpy()
    both = opposite & k2match
    supports = bool(np.mean(opposite) >= 2.0 / 3.0 and np.mean(k2match) >= 2.0 / 3.0)
    return {
        "Subset": subset,
        "Rows": len(df),
        "OppositeSignRows": int(np.sum(opposite)),
        "OppositeSignFraction": float(np.mean(opposite)),
        "K2MatchesSourceSplitRows": int(np.sum(k2match)),
        "K2MatchesSourceSplitFraction": float(np.mean(k2match)),
        "AntiAlignedAndK2MatchedRows": int(np.sum(both)),
        "AntiAlignedAndK2MatchedFraction": float(np.mean(both)),
        "MeanAbsSN": float(np.mean(np.abs(df["SNStandardizedResidual"].to_numpy(float)))),
        "MeanAbsBAO": float(np.mean(np.abs(df["BAOStandardizedResidual"].to_numpy(float)))),
        "MeanSignedChannelProduct": float(
            np.mean(df["SNStandardizedResidual"].to_numpy(float) * df["BAOStandardizedResidual"].to_numpy(float))
        ),
        "SupportsATau2Prior": supports,
        "Interpretation": "anti_alignment_supports_source_split_gain_prior"
        if supports
        else "anti_alignment_not_stable_in_this_subset",
        "ClaimBoundary": "source_split_antialignment_preflight_no_measurement_validation",
    }


def main() -> None:
    df = pd.read_csv(DECOMP).copy()
    df["SNSign"] = [sign(v) for v in df["SNStandardizedResidual"]]
    df["BAOSign"] = [sign(v) for v in df["BAOStandardizedResidual"]]
    df["SourceSplitSign"] = [sign(v) for v in df["SourceSplitResponse"]]
    df["K2Sign"] = [sign(v) for v in df["K2LockedRho4"]]
    df["SNBAOOppositeSign"] = (df["SNSign"] * df["BAOSign"]) < 0
    df["SNBAOSameSign"] = (df["SNSign"] * df["BAOSign"]) > 0
    df["K2MatchesSourceSplitSign"] = df["K2Sign"] == df["SourceSplitSign"]
    df["ChannelProduct"] = df["SNStandardizedResidual"] * df["BAOStandardizedResidual"]
    df["AntiAlignmentClass"] = np.where(
        df["SNBAOOppositeSign"] & df["K2MatchesSourceSplitSign"],
        "OPPOSED_CHANNELS_AND_K2_SIGN_MATCH",
        np.where(df["SNBAOOppositeSign"], "OPPOSED_CHANNELS_ONLY", "NOT_OPPOSED"),
    )
    df["ClaimBoundary"] = "source_split_antialignment_preflight_no_measurement_validation"

    cols = [
        "GridIndex",
        "z_grid",
        "x_coordinate",
        "DepthBin",
        "SignStableTemplate",
        "SNStandardizedResidual",
        "BAOStandardizedResidual",
        "SourceSplitResponse",
        "K2LockedRho4",
        "SNSign",
        "BAOSign",
        "SourceSplitSign",
        "K2Sign",
        "SNBAOOppositeSign",
        "K2MatchesSourceSplitSign",
        "ChannelProduct",
        "AntiAlignmentClass",
        "ClaimBoundary",
    ]
    df[cols].to_csv(OUT, index=False)

    stable = df["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"])
    subsets = [
        ("all_points", df),
        ("sign_stable_only", df[stable]),
        ("low_depth", df[df["DepthBin"] == "low_depth"]),
        ("mid_depth", df[df["DepthBin"] == "mid_depth"]),
        ("high_depth", df[df["DepthBin"] == "high_depth"]),
        ("mid_high_depth", df[df["DepthBin"].isin(["mid_depth", "high_depth"])]),
    ]
    pd.DataFrame([summarize(sub, name) for name, sub in subsets]).to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
