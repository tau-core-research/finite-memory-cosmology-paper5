#!/usr/bin/env python3
"""Check whether AS_DECLARED alpha subtraction removes K2-relevant structure.

This is a preflight diagnostic only. It does not refit K1, does not change the
locked K2 kernel, and does not authorize a measurement claim.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
ALPHA = EVIDENCE / "alpha_as_declared_preflight.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
BRANCH_SIGMA = EVIDENCE / "source_split_likelihood_native_branch_scatter_covariance.csv"

OUT = EVIDENCE / "alpha_subtracted_k2_residual_check.csv"
SUMMARY = EVIDENCE / "alpha_subtracted_k2_residual_summary.csv"


def sign(value: float) -> int:
    if not math.isfinite(value) or abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def rms(v: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(v, dtype=float) ** 2)))


def mean_abs(v: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(v, dtype=float))))


def chi2_diag(y: np.ndarray, m: np.ndarray, sigma: np.ndarray) -> float:
    usable = np.isfinite(y) & np.isfinite(m) & np.isfinite(sigma) & (sigma > 0)
    if not np.any(usable):
        return float("nan")
    r = (y[usable] - m[usable]) / sigma[usable]
    return float(np.dot(r, r))


def k2_locked_from_k1(x: np.ndarray, k1: np.ndarray, rho: float = 4.0) -> np.ndarray:
    return np.asarray(k1, dtype=float) * (1.0 + float(rho) * np.asarray(x, dtype=float) ** 3)


def metric_block(y: np.ndarray, k1: np.ndarray, k2: np.ndarray, sigma: np.ndarray, prefix: str) -> dict[str, float]:
    return {
        f"{prefix}RMS": rms(y),
        f"{prefix}CosineVsK1": cosine(y, k1),
        f"{prefix}CosineVsK2": cosine(y, k2),
        f"{prefix}MeanAbsResidualVsK1": mean_abs(y - k1),
        f"{prefix}MeanAbsResidualVsK2": mean_abs(y - k2),
        f"{prefix}Chi2DiagVsK1": chi2_diag(y, k1, sigma),
        f"{prefix}Chi2DiagVsK2": chi2_diag(y, k2, sigma),
    }


def main() -> None:
    target = pd.read_csv(TARGET)
    alpha = pd.read_csv(ALPHA)
    k1 = pd.read_csv(K1)
    sigma = pd.read_csv(BRANCH_SIGMA)[["GridIndex", "SigmaMaxNativeScatter"]]

    usable_target = target[
        target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
        & target["SourceSplitResponse"].notna()
    ][["GridIndex", "z_grid", "SourceSplitResponse", "SignStableTemplate"]]

    base = (
        usable_target.merge(
            k1[["GridIndex", "x_coordinate", "K1Response"]],
            on="GridIndex",
            how="inner",
        )
        .merge(sigma, on="GridIndex", how="left")
        .sort_values("GridIndex")
    )
    base["K2LockedRho4"] = k2_locked_from_k1(base["x_coordinate"], base["K1Response"], rho=4.0)

    rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    for extraction_id, group in alpha.groupby("ExtractionID"):
        merged = base.merge(
            group[["GridIndex", "Alpha", "ClumpinessAmplitude", "AlphaASDeclaredPreview"]],
            on="GridIndex",
            how="inner",
        ).sort_values("GridIndex")

        y = merged["SourceSplitResponse"].to_numpy(float)
        a = merged["AlphaASDeclaredPreview"].to_numpy(float)
        y_after = y - a
        k1_vec = merged["K1Response"].to_numpy(float)
        k2_vec = merged["K2LockedRho4"].to_numpy(float)
        sig = merged["SigmaMaxNativeScatter"].to_numpy(float)
        stable = merged["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy()

        for _, row in merged.iterrows():
            alpha_preview = float(row["AlphaASDeclaredPreview"])
            residual_after = float(row["SourceSplitResponse"] - alpha_preview)
            k2_pred = float(row["K2LockedRho4"])
            rows.append(
                {
                    "CheckID": "ALPHA_SUBTRACTED_K2_RESIDUAL_PREFLIGHT_V1",
                    "ExtractionID": extraction_id,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_k1_coordinate": float(row["x_coordinate"]),
                    "Alpha": float(row["Alpha"]),
                    "ClumpinessAmplitude": float(row["ClumpinessAmplitude"]),
                    "SourceSplitResponse": float(row["SourceSplitResponse"]),
                    "AlphaASDeclaredPreview": alpha_preview,
                    "ResidualAfterAlpha": residual_after,
                    "K1Response": float(row["K1Response"]),
                    "K2LockedRho4": k2_pred,
                    "SigmaDiagProxy": float(row["SigmaMaxNativeScatter"]),
                    "OriginalMinusK2": float(row["SourceSplitResponse"] - k2_pred),
                    "ResidualAfterAlphaMinusK2": float(residual_after - k2_pred),
                    "OriginalSign": sign(float(row["SourceSplitResponse"])),
                    "ResidualAfterAlphaSign": sign(residual_after),
                    "K2Sign": sign(k2_pred),
                    "SignStableTemplate": bool(row["SignStableTemplate"]),
                    "AlphaChangesTargetSign": sign(float(row["SourceSplitResponse"])) != sign(residual_after),
                    "ClaimBoundary": "alpha_subtraction_prefight_no_measurement_validation",
                }
            )

        summary: dict[str, object] = {
            "SummaryID": "ALPHA_SUBTRACTED_K2_RESIDUAL_SUMMARY",
            "ExtractionID": extraction_id,
            "Rows": len(merged),
            "SignStableRows": int(np.sum(stable)),
            "AlphaPreviewRMS": rms(a),
            "TargetRMS": rms(y),
            "ResidualAfterAlphaRMS": rms(y_after),
            "AlphaRemovedRMSFraction": rms(a) / rms(y) if rms(y) > 0 else float("nan"),
            "TargetVsResidualAfterAlphaCosine": cosine(y, y_after),
            "AlphaChangesAnyTargetSign": bool(np.any([sign(yy) != sign(rr) for yy, rr in zip(y, y_after, strict=True)])),
            "Interpretation": "alpha_subtraction_barely_changes_source_split_target"
            if rms(a) / rms(y) < 0.1 and cosine(y, y_after) > 0.99
            else "alpha_subtraction_materially_changes_source_split_target",
            "ClaimBoundary": "alpha_subtraction_prefight_no_measurement_validation",
        }
        summary.update(metric_block(y, k1_vec, k2_vec, sig, "Original"))
        summary.update(metric_block(y_after, k1_vec, k2_vec, sig, "AfterAlpha"))
        summary["DeltaCosineVsK2AfterAlpha"] = float(summary["AfterAlphaCosineVsK2"] - summary["OriginalCosineVsK2"])
        summary["DeltaMeanAbsVsK2AfterAlpha"] = float(summary["AfterAlphaMeanAbsResidualVsK2"] - summary["OriginalMeanAbsResidualVsK2"])
        summary["DeltaChi2VsK2AfterAlpha"] = float(summary["AfterAlphaChi2DiagVsK2"] - summary["OriginalChi2DiagVsK2"])

        if np.any(stable):
            stable_summary = metric_block(y[stable], k1_vec[stable], k2_vec[stable], sig[stable], "StableOriginal")
            stable_summary.update(metric_block(y_after[stable], k1_vec[stable], k2_vec[stable], sig[stable], "StableAfterAlpha"))
            summary.update(stable_summary)
            summary["StableDeltaCosineVsK2AfterAlpha"] = float(
                summary["StableAfterAlphaCosineVsK2"] - summary["StableOriginalCosineVsK2"]
            )

        summaries.append(summary)

    pd.DataFrame(rows).to_csv(OUT, index=False)
    pd.DataFrame(summaries).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
