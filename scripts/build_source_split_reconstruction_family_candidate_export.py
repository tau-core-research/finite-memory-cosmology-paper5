#!/usr/bin/env python3
"""Build the source-split reconstruction-family candidate export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT_DIR = ROOT / "data" / "reconstruction_families"
OUT = OUT_DIR / "source_split_reconstruction_family_responses.csv"

SN = EVIDENCE / "source_split_sn_branch_export_handoff.csv"
BAO = EVIDENCE / "source_split_bao_branch_export_handoff.csv"

EXPORT_COLUMNS = [
    "ExportID",
    "FamilyID",
    "FamilyType",
    "SourceProductID",
    "TargetID",
    "GridIndex",
    "z_grid",
    "x_coordinate",
    "x_mapping",
    "ResponseValue",
    "ResponseSigma",
    "ResponseSign",
    "CoordinateNative",
    "UsesPublicSN",
    "UsesPublicBAO",
    "FittedInThisNote",
    "ClaimBoundary",
]


def normalize_handoff(df: pd.DataFrame) -> pd.DataFrame:
    ready = df[df["ReadyForCandidateExport"].astype(str).str.lower().eq("true")].copy()
    output = pd.DataFrame(
        {
            "ExportID": ready["ExportID"],
            "FamilyID": ready["CandidateFamilyID"],
            "FamilyType": ready["FamilyType"],
            "SourceProductID": ready["SourceProductID"],
            "TargetID": ready["TargetID"],
            "GridIndex": ready["GridIndex"].astype(int),
            "z_grid": ready["z_grid"].astype(float),
            "x_coordinate": ready["x_coordinate"].astype(float),
            "x_mapping": ready["x_mapping"],
            "ResponseValue": ready["CandidateResponseValue"].astype(float),
            "ResponseSigma": ready["CandidateResponseSigma"].astype(float),
            "ResponseSign": ready["CandidateResponseSign"].astype(int),
            "CoordinateNative": ready["CoordinateNative"].astype(bool),
            "UsesPublicSN": ready["UsesPublicSN"].astype(bool),
            "UsesPublicBAO": ready["UsesPublicBAO"].astype(bool),
            "FittedInThisNote": ready["FittedInThisNote"].astype(bool),
            "ClaimBoundary": "candidate_export_benchmark_input_only_no_measurement_claim",
        }
    )
    return output[EXPORT_COLUMNS]


def main() -> None:
    sn = normalize_handoff(pd.read_csv(SN))
    bao = normalize_handoff(pd.read_csv(BAO))
    export = pd.concat([sn, bao], ignore_index=True)
    export = export.sort_values(["FamilyID", "GridIndex"]).reset_index(drop=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    export.to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
