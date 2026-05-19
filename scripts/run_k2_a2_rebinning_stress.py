#!/usr/bin/env python3
"""Rebinning stress test for locked K2_SOURCE_SPLIT_A2_PRIOR_V1.

This aggregates the reconstruction-family source-split target and the locked
prediction into predeclared coarse bins. It is a robustness preflight only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

SOURCE = EVIDENCE / "k2_a2_reconstruction_family_benchmark.csv"
OUT = EVIDENCE / "k2_a2_rebinning_stress.csv"
SUMMARY = EVIDENCE / "k2_a2_rebinning_stress_summary.csv"


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def chi2_diag(y: np.ndarray, pred: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(pred) & np.isfinite(sigma) & (sigma > 0.0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - pred[usable]) / sigma[usable]
    return float(np.dot(r, r))


def weighted_mean(values: pd.Series, sigma: pd.Series) -> float:
    weights = 1.0 / np.maximum(sigma.to_numpy(float), 1e-12) ** 2
    return float(np.sum(values.to_numpy(float) * weights) / np.sum(weights))


def combined_sigma(sigma: pd.Series) -> float:
    weights = 1.0 / np.maximum(sigma.to_numpy(float), 1e-12) ** 2
    return float(np.sqrt(1.0 / np.sum(weights)))


def make_scheme_rows(df: pd.DataFrame, scheme_id: str, assignments: dict[int, str]) -> pd.DataFrame:
    work = df.copy()
    work["RebinSchemeID"] = scheme_id
    work["RebinID"] = [assignments[int(g)] for g in work["GridIndex"]]
    rows: list[dict[str, object]] = []
    for rebin_id, sub in work.groupby("RebinID", sort=False):
        sigma = sub["FamilySourceSplitSigmaDiag"]
        rows.append(
            {
                "RebinSchemeID": scheme_id,
                "RebinID": rebin_id,
                "Rows": len(sub),
                "GridIndices": ";".join(str(int(v)) for v in sub["GridIndex"]),
                "MeanZ": float(sub["z_grid"].mean()),
                "MeanX": float(sub["x_coordinate"].mean()),
                "FamilySourceSplitResponse": weighted_mean(sub["FamilySourceSplitResponse"], sigma),
                "FamilySourceSplitSigmaDiag": combined_sigma(sigma),
                "K1Response": weighted_mean(sub["K1Response"], sigma),
                "K2UnitLockedRho4": weighted_mean(sub["K2UnitLockedRho4"], sigma),
                "K2SourceSplitA2Prediction": weighted_mean(sub["K2SourceSplitA2Prediction"], sigma),
                "AntiAlignedFraction": float(sub["SNBAOOppositeSign"].mean()),
                "DominantDepthBin": sub["DepthBin"].mode().iloc[0],
                "ClaimBoundary": "rebinning_stress_preflight_no_measurement_validation",
            }
        )
    return pd.DataFrame(rows)


def summarize(rebinned: pd.DataFrame, scheme_id: str) -> list[dict[str, object]]:
    rows = []
    y = rebinned["FamilySourceSplitResponse"].to_numpy(float)
    sigma = rebinned["FamilySourceSplitSigmaDiag"].to_numpy(float)
    models = [
        ("K1_NO_MEMORY", rebinned["K1Response"].to_numpy(float)),
        ("K2_UNIT_LOCKED_RHO4", rebinned["K2UnitLockedRho4"].to_numpy(float)),
        ("K2_SOURCE_SPLIT_A2_PRIOR_V1", rebinned["K2SourceSplitA2Prediction"].to_numpy(float)),
    ]
    a2_chi = None
    unit_chi = None
    for model_id, pred in models:
        c2 = chi2_diag(y, pred, sigma)
        if model_id == "K2_SOURCE_SPLIT_A2_PRIOR_V1":
            a2_chi = c2
        if model_id == "K2_UNIT_LOCKED_RHO4":
            unit_chi = c2
        rows.append(
            {
                "RebinSchemeID": scheme_id,
                "ModelID": model_id,
                "Bins": len(rebinned),
                "PredictionToTargetRMSRatio": rms(pred) / rms(y) if rms(y) > 0.0 else float("nan"),
                "CosineTargetVsPrediction": cosine(y, pred),
                "ResidualRMS": rms(y - pred),
                "Chi2DiagProxy": c2,
                "SignMatchFraction": float(np.mean(np.sign(y) == np.sign(pred))),
                "ClaimBoundary": "rebinning_stress_preflight_no_measurement_validation",
            }
        )
    for row in rows:
        row["DeltaChi2VsA2"] = row["Chi2DiagProxy"] - float(a2_chi)
        row["DeltaChi2VsUnit"] = row["Chi2DiagProxy"] - float(unit_chi)
    return rows


def main() -> None:
    df = pd.read_csv(SOURCE)
    # Predeclared coarse schemes over the existing eight row-aligned points.
    schemes = {
        "DEPTH_THREE_BIN": {
            0: "low",
            1: "low",
            2: "mid",
            3: "mid",
            4: "mid",
            5: "high",
            6: "high",
            8: "high",
        },
        "PAIRWISE_ADJACENT": {
            0: "pair_0_1",
            1: "pair_0_1",
            2: "pair_2_3",
            3: "pair_2_3",
            4: "pair_4_5",
            5: "pair_4_5",
            6: "pair_6_8",
            8: "pair_6_8",
        },
        "MEMORY_ACTIVE_VS_LOW": {
            0: "low",
            1: "low",
            2: "memory_active",
            3: "memory_active",
            4: "memory_active",
            5: "memory_active",
            6: "memory_active",
            8: "memory_active",
        },
        "ANTI_ALIGNED_VS_OTHER": {
            int(row.GridIndex): "anti_aligned" if bool(row.SNBAOOppositeSign) else "other"
            for row in df.itertuples()
        },
    }

    all_rebinned = []
    summary_rows: list[dict[str, object]] = []
    for scheme_id, assignments in schemes.items():
        rebinned = make_scheme_rows(df, scheme_id, assignments)
        all_rebinned.append(rebinned)
        summary_rows.extend(summarize(rebinned, scheme_id))

    pd.concat(all_rebinned, ignore_index=True).to_csv(OUT, index=False)
    summary = pd.DataFrame(summary_rows)
    best = summary.sort_values(["RebinSchemeID", "Chi2DiagProxy"]).groupby("RebinSchemeID", as_index=False).first()
    summary["BestModelByScheme"] = summary["RebinSchemeID"].map(dict(zip(best["RebinSchemeID"], best["ModelID"], strict=True)))
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
