#!/usr/bin/env python3
"""Decompose the public rerun target into SN and BAO branch contributions.

The current candidate target is y_split = L_SN r_SN - L_BAO r_BAO. This script
compares that branch construction to the earlier coordinate-native standardized
target to identify where sign flips and scale compression enter.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE = ROOT / "evidence"

SN_RESID = DATA / "residuals" / "sn_cmb_only_raw_residual_v1.csv"
BAO_RESID = DATA / "residuals" / "bao_cmb_only_log_residual_v1.csv"
L_SN = DATA / "transforms" / "k2_a2_l_sn_transform_v1.csv"
L_BAO = DATA / "transforms" / "k2_a2_l_bao_transform_v1.csv"
RERUN = EVIDENCE / "likelihood_native_rerun_candidate_vector.csv"
COORD_TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
TARGET_CONSTRUCTION = EVIDENCE / "public_rerun_target_construction_audit.csv"

OUT_AUDIT = EVIDENCE / "public_rerun_branch_contribution_audit.csv"
OUT_SUMMARY = EVIDENCE / "public_rerun_branch_contribution_summary.csv"


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


def load_transform(path: Path) -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(path)
    grid = df["GridIndex"].to_numpy(int)
    matrix = df.drop(columns=["GridIndex"]).to_numpy(float)
    return grid, matrix


def main() -> None:
    sn = pd.read_csv(SN_RESID)
    bao = pd.read_csv(BAO_RESID)
    rerun = pd.read_csv(RERUN)
    coord = pd.read_csv(COORD_TARGET)
    construction = pd.read_csv(TARGET_CONSTRUCTION)

    sn_grid, l_sn = load_transform(L_SN)
    bao_grid, l_bao = load_transform(L_BAO)
    if list(sn_grid) != list(bao_grid):
        raise ValueError("SN and BAO transform grids differ")

    r_sn = sn["RawResidualMu"].to_numpy(float)
    r_bao = bao["LogResidual"].to_numpy(float)
    sn_component = l_sn @ r_sn
    bao_component = l_bao @ r_bao
    candidate_rebuilt = sn_component - bao_component

    rows = pd.DataFrame(
        {
            "GridIndex": sn_grid,
            "SNComponentRawProjected": sn_component,
            "BAOComponentLogProjected": bao_component,
            "CandidateRebuilt": candidate_rebuilt,
        }
    )
    rows = rows.merge(
        rerun[
            [
                "GridIndex",
                "z_grid",
                "x_coordinate",
                "SourceSplitCandidate",
                "K1Response",
                "K2LockedA2Prediction",
            ]
        ],
        on="GridIndex",
        how="left",
    )
    rows = rows.merge(
        coord[
            [
                "GridIndex",
                "SourceSplitResponse",
                "SNStandardizedResidual",
                "BAOStandardizedResidual",
                "SNBAOSameSign",
                "SignStableTemplate",
            ]
        ].rename(columns={"SourceSplitResponse": "CoordinateNativeTarget"}),
        on="GridIndex",
        how="left",
    )
    rows = rows.merge(
        construction[["GridIndex", "TargetConstructionClass", "CandidateVsCoordinateSignMismatch"]],
        on="GridIndex",
        how="left",
    )

    rows["RebuildError"] = rows["CandidateRebuilt"] - rows["SourceSplitCandidate"]
    rows["RawSNMinusBAOSign"] = [sign(v) for v in rows["CandidateRebuilt"]]
    rows["StandardizedSNMinusBAOSign"] = [sign(v) for v in rows["CoordinateNativeTarget"]]
    rows["SNComponentSign"] = [sign(v) for v in rows["SNComponentRawProjected"]]
    rows["BAOComponentSign"] = [sign(v) for v in rows["BAOComponentLogProjected"]]
    rows["SNStandardizedSign"] = [sign(v) for v in rows["SNStandardizedResidual"]]
    rows["BAOStandardizedSign"] = [sign(v) for v in rows["BAOStandardizedResidual"]]
    rows["ProjectedVsStandardizedSignMismatch"] = rows["RawSNMinusBAOSign"] != rows["StandardizedSNMinusBAOSign"]
    rows["SNBranchSignChanged"] = rows["SNComponentSign"] != rows["SNStandardizedSign"]
    rows["BAOBranchSignChanged"] = rows["BAOComponentSign"] != rows["BAOStandardizedSign"]
    rows["AbsSNComponent"] = np.abs(rows["SNComponentRawProjected"])
    rows["AbsBAOComponent"] = np.abs(rows["BAOComponentLogProjected"])
    rows["AbsCoordinateTarget"] = np.abs(rows["CoordinateNativeTarget"])
    rows["AbsCandidate"] = np.abs(rows["SourceSplitCandidate"])
    rows["CandidateOverCoordinate"] = safe_ratio(
        rows["SourceSplitCandidate"].to_numpy(float),
        rows["CoordinateNativeTarget"].to_numpy(float),
    )
    rows["AbsCandidateOverAbsCoordinate"] = safe_ratio(
        rows["AbsCandidate"].to_numpy(float),
        rows["AbsCoordinateTarget"].to_numpy(float),
    )
    rows["BAOShareOfAbsBranches"] = safe_ratio(
        rows["AbsBAOComponent"].to_numpy(float),
        (rows["AbsSNComponent"] + rows["AbsBAOComponent"]).to_numpy(float),
    )
    rows["SNShareOfAbsBranches"] = safe_ratio(
        rows["AbsSNComponent"].to_numpy(float),
        (rows["AbsSNComponent"] + rows["AbsBAOComponent"]).to_numpy(float),
    )

    classes = []
    for _, row in rows.iterrows():
        cls: list[str] = []
        if row["ProjectedVsStandardizedSignMismatch"]:
            cls.append("PROJECTED_TARGET_SIGN_DIFFERS_FROM_STANDARDIZED_TARGET")
        if row["SNBranchSignChanged"]:
            cls.append("SN_BRANCH_SIGN_CHANGED_BY_RAW_PROJECTION")
        if row["BAOBranchSignChanged"]:
            cls.append("BAO_BRANCH_SIGN_CHANGED_BY_LOG_PROJECTION")
        if np.isfinite(row["AbsCandidateOverAbsCoordinate"]) and row["AbsCandidateOverAbsCoordinate"] < 0.5:
            cls.append("RAW_PROJECTED_TARGET_COMPRESSED")
        if row["BAOShareOfAbsBranches"] > 0.65:
            cls.append("BAO_BRANCH_DOMINANT")
        if row["SNShareOfAbsBranches"] > 0.65:
            cls.append("SN_BRANCH_DOMINANT")
        if not cls:
            cls.append("BALANCED_OR_MINOR_BRANCH_EFFECT")
        classes.append(";".join(cls))
    rows["BranchConstructionClass"] = classes
    rows["MeasurementValidationAllowed"] = False
    rows["ClaimBoundary"] = "public_rerun_branch_contribution_no_measurement_validation"
    rows.to_csv(OUT_AUDIT, index=False)

    sign_mismatch = rows[rows["ProjectedVsStandardizedSignMismatch"]]
    compressed = rows[rows["BranchConstructionClass"].str.contains("RAW_PROJECTED_TARGET_COMPRESSED", na=False)]
    sn_changed = rows[rows["SNBranchSignChanged"]]
    bao_changed = rows[rows["BAOBranchSignChanged"]]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PUBLIC_RERUN_BRANCH_CONTRIBUTION_OVERVIEW",
                "Rows": len(rows),
                "MaxRebuildAbsError": float(np.max(np.abs(rows["RebuildError"]))),
                "ProjectedVsStandardizedSignMismatchRows": len(sign_mismatch),
                "SNBranchSignChangedRows": len(sn_changed),
                "BAOBranchSignChangedRows": len(bao_changed),
                "RawProjectedTargetCompressedRows": len(compressed),
                "MedianAbsCandidateOverAbsCoordinate": float(np.nanmedian(rows["AbsCandidateOverAbsCoordinate"])),
                "MedianBAOShareOfAbsBranches": float(np.nanmedian(rows["BAOShareOfAbsBranches"])),
                "MedianSNShareOfAbsBranches": float(np.nanmedian(rows["SNShareOfAbsBranches"])),
                "SignMismatchGridIndices": ";".join(sign_mismatch["GridIndex"].astype(str)),
                "CompressedGridIndices": ";".join(compressed["GridIndex"].astype(str)),
                "SNChangedGridIndices": ";".join(sn_changed["GridIndex"].astype(str)),
                "BAOChangedGridIndices": ";".join(bao_changed["GridIndex"].astype(str)),
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "PUBLIC_RERUN_TENSION_LOCALIZED_TO_RAW_PROJECTED_BRANCH_TARGET",
                "StrongestAllowedClaim": "the public rerun target tension is localized to raw projected branch construction versus standardized source-split target",
                "NextAction": "audit whether the final measurement route should use raw residual projection, standardized branch contrast, or a declared whitening transform before scoring A2",
                "ClaimBoundary": "public_rerun_branch_contribution_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
