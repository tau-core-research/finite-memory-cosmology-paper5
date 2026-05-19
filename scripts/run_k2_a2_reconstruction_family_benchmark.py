#!/usr/bin/env python3
"""Benchmark locked K2_A2 against reconstruction-family branch responses.

This uses the exported SN and BAO branch response family as the target source,
then forms R_split = SN_branch - BAO_branch. It is still a preflight benchmark,
not a public covariance-aware measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"

FAMILY = DATA / "reconstruction_families" / "source_split_reconstruction_family_responses.csv"
PRED = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"

OUT = EVIDENCE / "k2_a2_reconstruction_family_benchmark.csv"
SUMMARY = EVIDENCE / "k2_a2_reconstruction_family_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def chi2_diag(y: np.ndarray, m: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(m) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - m[usable]) / sigma[usable]
    return float(np.dot(r, r))


def aic(chi2: float, k: int = 0) -> float:
    return float(chi2 + 2 * k)


def depth_regime_to_bin(regime: str) -> str:
    if str(regime).startswith("low"):
        return "low_depth"
    if str(regime).startswith("mid"):
        return "mid_depth"
    return "high_depth"


def metrics(sub: pd.DataFrame, model_id: str, pred_col: str, k: int = 0) -> dict[str, object]:
    y = sub["FamilySourceSplitResponse"].to_numpy(float)
    pred = sub[pred_col].to_numpy(float)
    sigma = sub["FamilySourceSplitSigmaDiag"].to_numpy(float)
    c2 = chi2_diag(y, pred, sigma)
    return {
        "ModelID": model_id,
        "Rows": len(sub),
        "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
        "CosineTargetVsPrediction": cosine(y, pred),
        "ResidualRMS": rms(y - pred),
        "Chi2DiagProxy": c2,
        "AIC": aic(c2, k),
        "SignMatchFraction": float(np.mean(np.sign(y) == np.sign(pred))),
    }


def summarize(subset: str, sub: pd.DataFrame) -> list[dict[str, object]]:
    rows = [
        metrics(sub, "K1_NO_MEMORY", "K1Response", 0),
        metrics(sub, "K2_UNIT_LOCKED_RHO4", "K2UnitLockedRho4", 0),
        metrics(sub, "K2_SOURCE_SPLIT_A2_PRIOR_V1", "K2SourceSplitA2Prediction", 0),
    ]
    out = []
    a2_aic = next(row["AIC"] for row in rows if row["ModelID"] == "K2_SOURCE_SPLIT_A2_PRIOR_V1")
    unit_aic = next(row["AIC"] for row in rows if row["ModelID"] == "K2_UNIT_LOCKED_RHO4")
    for row in rows:
        row["Subset"] = subset
        row["DeltaAICVsA2"] = row["AIC"] - a2_aic
        row["DeltaAICVsUnit"] = row["AIC"] - unit_aic
        row["ClaimBoundary"] = "reconstruction_family_preflight_no_measurement_validation"
        out.append(row)
    return out


def main() -> None:
    family = pd.read_csv(FAMILY)
    pred = pd.read_csv(PRED)

    pivot = family.pivot_table(
        index=["GridIndex", "z_grid"],
        columns="FamilyType",
        values=["ResponseValue", "ResponseSigma"],
        aggfunc="first",
    )
    pivot.columns = ["_".join(col).strip() for col in pivot.columns.to_flat_index()]
    pivot = pivot.reset_index()
    pivot["FamilySourceSplitResponse"] = pivot["ResponseValue_SN_branch"] - pivot["ResponseValue_BAO_branch"]
    pivot["FamilySourceSplitSigmaDiag"] = np.sqrt(
        pivot["ResponseSigma_SN_branch"].astype(float) ** 2 + pivot["ResponseSigma_BAO_branch"].astype(float) ** 2
    )
    pivot["SNBAOOppositeSign"] = np.sign(pivot["ResponseValue_SN_branch"]) != np.sign(pivot["ResponseValue_BAO_branch"])

    merged = pivot.merge(
        pred[
            [
                "GridIndex",
                "x_coordinate",
                "K1Response",
                "K2UnitLockedRho4",
                "K2SourceSplitA2Prediction",
                "TargetRegime",
                "PredictionStatus",
            ]
        ],
        on="GridIndex",
        how="inner",
    ).sort_values("GridIndex")
    merged["DepthBin"] = [depth_regime_to_bin(value) for value in merged["TargetRegime"]]
    merged["A2Residual"] = merged["FamilySourceSplitResponse"] - merged["K2SourceSplitA2Prediction"]
    merged["A2ExplainedFractionProxy"] = 1.0 - (
        np.abs(merged["A2Residual"]) / np.abs(merged["FamilySourceSplitResponse"])
    )
    merged["ClaimBoundary"] = "reconstruction_family_preflight_no_measurement_validation"
    merged.to_csv(OUT, index=False)

    rows: list[dict[str, object]] = []
    subsets = [
        ("all_points", merged),
        ("low_depth", merged[merged["DepthBin"] == "low_depth"]),
        ("mid_depth", merged[merged["DepthBin"] == "mid_depth"]),
        ("high_depth", merged[merged["DepthBin"] == "high_depth"]),
        ("mid_high_depth", merged[merged["DepthBin"].isin(["mid_depth", "high_depth"])]),
        ("anti_aligned", merged[merged["SNBAOOppositeSign"]]),
        ("anti_aligned_mid_high", merged[merged["SNBAOOppositeSign"] & merged["DepthBin"].isin(["mid_depth", "high_depth"])]),
    ]
    for subset, sub in subsets:
        if len(sub) >= 2:
            rows.extend(summarize(subset, sub.copy()))

    summary = pd.DataFrame(rows)
    best = summary.sort_values(["Subset", "AIC"]).groupby("Subset", as_index=False).first()
    summary["BestAICModelBySubset"] = summary["Subset"].map(dict(zip(best["Subset"], best["ModelID"], strict=True)))
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
