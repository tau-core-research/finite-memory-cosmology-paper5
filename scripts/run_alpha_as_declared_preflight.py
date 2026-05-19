#!/usr/bin/env python3
"""Run an AS_DECLARED-only alpha optical-null preflight.

This script uses the tau-core sign orientation:

    response_i = (1 - alpha) * optical_shape_i

It does not fit alpha, does not flip the sign by score, and does not authorize
measurement validation. It only reports whether the predeclared optical alpha
preview has sign/scale explanatory power on the current source-split target.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
PREVIEW = EVIDENCE / "physical_null_alpha_response_preview.csv"

OUT = EVIDENCE / "alpha_as_declared_preflight.csv"
SUMMARY = EVIDENCE / "alpha_as_declared_preflight_summary.csv"


def sign(value: float) -> int:
    if not math.isfinite(value) or abs(value) < 1e-12:
        return 0
    return 1 if value > 0 else -1


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 0.0:
        return float("nan")
    return float(np.dot(a, b) / denom)


def main() -> None:
    target = pd.read_csv(TARGET)
    preview = pd.read_csv(PREVIEW)
    usable = target[
        target["HasSNAndBAO"].astype(str).str.lower().isin(["true", "1", "yes"])
        & target["SourceSplitResponse"].notna()
    ].copy()

    rows: list[dict[str, object]] = []
    for extraction_id, group in preview.groupby("ExtractionID"):
        merged = usable.merge(
            group[["GridIndex", "Alpha", "ClumpinessAmplitude", "ResponsePreview", "ResponseSigmaDiagPreview"]],
            on="GridIndex",
            how="inner",
        ).sort_values("GridIndex")

        y = merged["SourceSplitResponse"].to_numpy(float)
        pred = merged["ResponsePreview"].to_numpy(float)
        stable = merged["SignStableTemplate"].astype(str).str.lower().isin(["true", "1", "yes"]).to_numpy()

        target_rms = float(np.sqrt(np.mean(y * y)))
        preview_rms = float(np.sqrt(np.mean(pred * pred)))
        rms_ratio = preview_rms / target_rms if target_rms > 0.0 else float("nan")
        best_forbidden_scale = float(np.dot(pred, y) / np.dot(pred, pred)) if float(np.dot(pred, pred)) > 0.0 else float("nan")

        sign_matches = [sign(p) == sign(t) for p, t in zip(pred, y, strict=True)]
        stable_matches = [m for m, is_stable in zip(sign_matches, stable, strict=True) if is_stable]

        for _, row in merged.iterrows():
            rows.append(
                {
                    "PreflightID": "ALPHA_AS_DECLARED_TAU_CORE_PREFLIGHT_V1",
                    "ExtractionID": extraction_id,
                    "GridIndex": int(row["GridIndex"]),
                    "z_grid": float(row["z_grid"]),
                    "x_coordinate": float(row["x_coordinate"]),
                    "Alpha": float(row["Alpha"]),
                    "ClumpinessAmplitude": float(row["ClumpinessAmplitude"]),
                    "SourceSplitResponse": float(row["SourceSplitResponse"]),
                    "AlphaASDeclaredPreview": float(row["ResponsePreview"]),
                    "PreviewSigmaDiag": float(row["ResponseSigmaDiagPreview"]),
                    "TargetSign": sign(float(row["SourceSplitResponse"])),
                    "PreviewSign": sign(float(row["ResponsePreview"])),
                    "SignMatchesTarget": sign(float(row["ResponsePreview"])) == sign(float(row["SourceSplitResponse"])),
                    "SignStableTemplate": bool(row["SignStableTemplate"]),
                    "ScoringAllowed": False,
                    "ClaimBoundary": "alpha_as_declared_preflight_no_measurement_validation",
                }
            )

        summary_row = {
            "SummaryID": "ALPHA_AS_DECLARED_TAU_CORE_PREFLIGHT_SUMMARY",
            "ExtractionID": extraction_id,
            "Rows": len(merged),
            "SignMatches": int(sum(sign_matches)),
            "SignMatchFraction": float(np.mean(sign_matches)) if sign_matches else 0.0,
            "SignStableRows": int(np.sum(stable)),
            "SignStableMatches": int(sum(stable_matches)),
            "SignStableMatchFraction": float(np.mean(stable_matches)) if stable_matches else 0.0,
            "TargetRMS": target_rms,
            "PreviewRMS": preview_rms,
            "PreviewToTargetRMSRatio": rms_ratio,
            "CosineSimilarity": cosine(pred, y),
            "ForbiddenBestLinearScaleDiagnosticOnly": best_forbidden_scale,
            "ScaleInterpretation": "alpha_preview_is_much_smaller_than_current_source_split_target"
            if rms_ratio < 0.25
            else "alpha_preview_scale_is_not_obviously_small",
            "TauCoreSignConvention": "AS_DECLARED",
            "ScoringAllowed": False,
            "Interpretation": "as-declared optical alpha preview is a weak partial sign/control explanation, not a measurement comparator",
            "ClaimBoundary": "alpha_as_declared_preflight_no_measurement_validation",
        }
        rows.append({**summary_row, "PreflightID": "SUMMARY_ROW_NOT_POINT"})

    point_rows = pd.DataFrame([row for row in rows if row.get("PreflightID") != "SUMMARY_ROW_NOT_POINT"])
    summary_rows = pd.DataFrame([row for row in rows if row.get("PreflightID") == "SUMMARY_ROW_NOT_POINT"])
    point_rows.to_csv(OUT, index=False)
    summary_rows.drop(columns=["PreflightID"]).to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
