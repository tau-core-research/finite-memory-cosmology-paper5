#!/usr/bin/env python3
"""Build row-level handoff for exporting the BAO residual branch candidate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"
JOINT = EVIDENCE / "source_split_joint_preflight.csv"
OUT = EVIDENCE / "source_split_bao_branch_export_handoff.csv"
SUMMARY = EVIDENCE / "source_split_bao_branch_export_handoff_summary.csv"


def sign(value: float) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def main() -> None:
    target = pd.read_csv(TARGET)
    joint = pd.read_csv(JOINT)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")]
    merged = usable.merge(
        joint[
            [
                "GridIndex",
                "BAONearestZ",
                "BAOAnchorRows",
                "BAOLogResidualMean",
                "BAOSigmaDiagProxy",
                "BAOAnchorDeltaZ",
                "BAOQuantities",
                "TransformStatus",
            ]
        ],
        on="GridIndex",
        how="left",
        validate="one_to_one",
    )

    rows = []
    for _, row in merged.iterrows():
        value = float(row["BAOStandardizedResidual"])
        sigma = 1.0
        missing = pd.isna(row["BAOLogResidualMean"]) or pd.isna(row["BAOStandardizedResidual"])
        rows.append(
            {
                "HandoffID": "RFAM_BAO_RESIDUAL_BRANCH_HANDOFF_V1",
                "CandidateFamilyID": "RFAM_BAO_RESIDUAL_BRANCH",
                "ExportID": "RF_SOURCE_SPLIT_CANDIDATE_V1",
                "FamilyType": "BAO_branch",
                "SourceProductID": "DESI_DR2_BAO_ALL_GAUSSIAN",
                "TargetID": row["TargetID"],
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(row["x_coordinate"]),
                "x_mapping": row["x_mapping"],
                "BAONearestZ": row["BAONearestZ"],
                "BAOAnchorRows": int(row["BAOAnchorRows"]) if not pd.isna(row["BAOAnchorRows"]) else 0,
                "BAOLogResidualMean": row["BAOLogResidualMean"],
                "BAOSigmaDiagProxy": row["BAOSigmaDiagProxy"],
                "BAOAnchorDeltaZ": row["BAOAnchorDeltaZ"],
                "BAOQuantities": row["BAOQuantities"],
                "BAOStandardizedResidual": row["BAOStandardizedResidual"],
                "CandidateResponseValue": value if not missing else "",
                "CandidateResponseSigma": sigma if not missing else "",
                "CandidateResponseSign": sign(value) if not missing else "",
                "CandidateColumnMapping": "ResponseValue=BAOStandardizedResidual; ResponseSigma=1.0 source-split standardized units",
                "CoordinateNative": True,
                "UsesPublicSN": False,
                "UsesPublicBAO": True,
                "FittedInThisNote": False,
                "ReadyForCandidateExport": not missing,
                "BlockingIssue": "" if not missing else "bao_branch_row_missing",
                "ClaimBoundary": "bao_branch_handoff_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "HandoffID": "RFAM_BAO_RESIDUAL_BRANCH_HANDOFF_V1",
                "Rows": len(output),
                "ReadyRows": int(output["ReadyForCandidateExport"].sum()),
                "MissingRows": int((~output["ReadyForCandidateExport"]).sum()),
                "CandidateFamilyID": "RFAM_BAO_RESIDUAL_BRANCH",
                "ResponseScale": "source_split_standardized_units",
                "CandidatePath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
                "AllowedForK2ScoringNow": False,
                "NextAction": "Append these BAO rows to the real candidate export together with the SN branch, then validate.",
                "ClaimBoundary": "bao_branch_handoff_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
