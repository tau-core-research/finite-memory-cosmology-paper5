#!/usr/bin/env python3
"""Compare the public rerun target against earlier source-split targets.

The goal is to identify whether the mixed/weakening rerun is tied to the
candidate target construction rather than to an A2 parameter change. This is a
diagnostic only; it does not alter targets or predictions.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"

RERUN = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COORD_TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
TENSION = EVIDENCE / "public_covariance_rerun_tension_axes_audit.csv"

OUT_AUDIT = EVIDENCE / "public_rerun_target_construction_audit.csv"
OUT_SUMMARY = EVIDENCE / "public_rerun_target_construction_summary.csv"


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def safe_ratio(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    out = np.full_like(a, np.nan, dtype=float)
    mask = np.abs(b) > 1e-12
    out[mask] = a[mask] / b[mask]
    return out


def main() -> None:
    rerun = pd.read_csv(RERUN)
    coord = pd.read_csv(COORD_TARGET)
    k1 = pd.read_csv(K1)
    tension = pd.read_csv(TENSION)

    coord = coord[coord["HasSNAndBAO"].astype(str).str.lower().eq("true")]
    merged = (
        rerun[
            [
                "GridIndex",
                "z_grid",
                "x_coordinate",
                "SourceSplitCandidate",
                "K1Response",
                "K2LockedA2Prediction",
                "CovarianceDiag",
            ]
        ]
        .merge(
            coord[
                [
                    "GridIndex",
                    "SourceSplitResponse",
                    "SNStandardizedResidual",
                    "BAOStandardizedResidual",
                    "SignStableTemplate",
                    "SNBAOSameSign",
                ]
            ].rename(columns={"SourceSplitResponse": "CoordinateNativeTarget"}),
            on="GridIndex",
            how="left",
        )
        .merge(
            k1[
                [
                    "GridIndex",
                    "K1Sigma",
                    "ControlResponseValue",
                    "NuisancePolicyID",
                    "CovariancePolicyID",
                ]
            ],
            on="GridIndex",
            how="left",
        )
        .merge(
            tension[["GridIndex", "PrimaryTensionAxes", "LocalATauRequiredForTarget"]],
            on="GridIndex",
            how="left",
        )
        .sort_values("GridIndex")
        .reset_index(drop=True)
    )

    candidate = merged["SourceSplitCandidate"].to_numpy(float)
    coord_target = merged["CoordinateNativeTarget"].to_numpy(float)
    k1_response = merged["K1Response"].to_numpy(float)
    k2_response = merged["K2LockedA2Prediction"].to_numpy(float)
    centered = merged["ControlResponseValue"].to_numpy(float)

    merged["CandidateSign"] = [sign(v) for v in candidate]
    merged["CoordinateTargetSign"] = [sign(v) for v in coord_target]
    merged["K1Sign"] = [sign(v) for v in k1_response]
    merged["K2Sign"] = [sign(v) for v in k2_response]
    merged["CandidateVsCoordinateSignMismatch"] = merged["CandidateSign"] != merged["CoordinateTargetSign"]
    merged["CandidateVsK1SignMismatch"] = merged["CandidateSign"] != merged["K1Sign"]
    merged["CandidateVsK2SignMismatch"] = merged["CandidateSign"] != merged["K2Sign"]
    merged["CandidateOverCoordinateTarget"] = safe_ratio(candidate, coord_target)
    merged["CandidateOverK1"] = safe_ratio(candidate, k1_response)
    merged["CandidateOverCenteredControl"] = safe_ratio(candidate, centered)
    merged["AbsCandidateOverAbsCoordinateTarget"] = safe_ratio(np.abs(candidate), np.abs(coord_target))
    merged["AbsCandidateOverAbsK2"] = safe_ratio(np.abs(candidate), np.abs(k2_response))
    merged["DeltaCandidateMinusCoordinateTarget"] = candidate - coord_target

    classes = []
    for _, row in merged.iterrows():
        row_classes: list[str] = []
        if row["CandidateVsCoordinateSignMismatch"]:
            row_classes.append("TARGET_SIGN_CHANGED_FROM_COORDINATE_NATIVE")
        if row["CandidateVsK2SignMismatch"]:
            row_classes.append("CANDIDATE_SIGN_OPPOSES_LOCKED_K2")
        if np.isfinite(row["AbsCandidateOverAbsCoordinateTarget"]) and row["AbsCandidateOverAbsCoordinateTarget"] < 0.5:
            row_classes.append("CANDIDATE_SCALE_COMPRESSED_VS_COORDINATE_NATIVE")
        if np.isfinite(row["AbsCandidateOverAbsK2"]) and row["AbsCandidateOverAbsK2"] < 0.5:
            row_classes.append("CANDIDATE_SCALE_BELOW_LOCKED_K2")
        if not row_classes:
            row_classes.append("TARGET_CONSTRUCTION_NOT_PRIMARY_ROW_ISSUE")
        classes.append(";".join(row_classes))
    merged["TargetConstructionClass"] = classes
    merged["MeasurementValidationAllowed"] = False
    merged["ClaimBoundary"] = "public_rerun_target_construction_no_measurement_validation"
    merged.to_csv(OUT_AUDIT, index=False)

    mismatch = merged[merged["CandidateVsCoordinateSignMismatch"]]
    k2_mismatch = merged[merged["CandidateVsK2SignMismatch"]]
    compressed = merged[merged["TargetConstructionClass"].str.contains("CANDIDATE_SCALE_COMPRESSED", na=False)]
    below_k2 = merged[merged["TargetConstructionClass"].str.contains("CANDIDATE_SCALE_BELOW_LOCKED_K2", na=False)]
    rows = [
        {
            "SummaryID": "PUBLIC_RERUN_TARGET_CONSTRUCTION_OVERVIEW",
            "Rows": len(merged),
            "CandidateCoordinateSignMismatchRows": len(mismatch),
            "CandidateK2SignMismatchRows": len(k2_mismatch),
            "CandidateScaleCompressedRows": len(compressed),
            "CandidateScaleBelowLockedK2Rows": len(below_k2),
            "MedianAbsCandidateOverAbsCoordinateTarget": float(
                np.nanmedian(merged["AbsCandidateOverAbsCoordinateTarget"])
            ),
            "MedianAbsCandidateOverAbsK2": float(np.nanmedian(merged["AbsCandidateOverAbsK2"])),
            "MeanAbsCandidateOverAbsK2": float(np.nanmean(merged["AbsCandidateOverAbsK2"])),
            "MismatchGridIndices": ";".join(mismatch["GridIndex"].astype(str)),
            "K2MismatchGridIndices": ";".join(k2_mismatch["GridIndex"].astype(str)),
            "CompressedGridIndices": ";".join(compressed["GridIndex"].astype(str)),
            "BelowK2GridIndices": ";".join(below_k2["GridIndex"].astype(str)),
            "MeasurementValidationAllowed": False,
            "CurrentStatus": "PUBLIC_RERUN_TARGET_CONSTRUCTION_IS_PRIMARY_TENSION_SOURCE",
            "StrongestAllowedClaim": "the mixed public rerun is strongly affected by target-construction sign and scale changes",
            "NextAction": "freeze target-construction convention before reading the mixed rerun as A2 evidence",
            "ClaimBoundary": "public_rerun_target_construction_no_measurement_validation",
        }
    ]
    pd.DataFrame(rows).to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
