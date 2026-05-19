#!/usr/bin/env python3
"""Build a coordinate-native public branch sign-family preflight artifact.

This fulfills TQ4 as a source-split sign-family preflight. It exports signs
from the public SN and BAO standardized branches on the coordinate-native
target rows. It is not a full reconstruction-family export and does not
authorize K2 scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = EVIDENCE / "source_split_public_sign_family.csv"
SUMMARY = EVIDENCE / "source_split_public_sign_family_summary.csv"


def sign(value: object) -> int:
    if pd.isna(value):
        return 0
    number = float(value)
    if number > 0.0:
        return 1
    if number < 0.0:
        return -1
    return 0


def main() -> None:
    df = pd.read_csv(SRC)
    rows = []
    for _, row in df.iterrows():
        has_row = bool(row["HasSNAndBAO"]) and pd.notna(row["SourceSplitResponse"])
        sn_sign = sign(row["SNStandardizedResidual"])
        bao_sign = sign(row["BAOStandardizedResidual"])
        split_sign = sign(row["SourceSplitResponse"])
        public_branch_stable = bool(has_row and sn_sign != 0 and bao_sign != 0 and sn_sign == bao_sign)
        public_branch_opposite = bool(has_row and sn_sign != 0 and bao_sign != 0 and sn_sign != bao_sign)
        rows.append(
            {
                "SignFamilyID": "SF_PUBLIC_SOURCE_SPLIT_FAMILIES",
                "SourceTargetID": row["TargetID"],
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(row["x_coordinate"]),
                "x_mapping": row["x_mapping"],
                "HasTargetRow": has_row,
                "SNBranchSign": sn_sign,
                "BAOBranchSign": bao_sign,
                "SourceSplitSign": split_sign,
                "PublicBranchSignStable": public_branch_stable,
                "PublicBranchOppositeSign": public_branch_opposite,
                "TemplateSignStable": bool(row["SignStableTemplate"]),
                "SNBAOSameSign": bool(row["SNBAOSameSign"]),
                "SignStableRule": "public SN and BAO standardized branch signs agree",
                "ReconstructionFamilies": "SN_standardized_branch;BAO_standardized_branch",
                "CoordinateNative": True,
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "AllowedForK2Scoring": False,
                "ExportStatus": "PUBLIC_BRANCH_SIGN_FAMILY_PREFLIGHT_NOT_RECONSTRUCTION_FAMILY",
                "BlockingIssue": "reconstruction_families_missing;not_full_public_reconstruction_family",
                "ClaimBoundary": "sign_family_preflight_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    usable = output[output["HasTargetRow"]]
    summary = pd.DataFrame(
        [
            {
                "SignFamilyID": "SF_PUBLIC_SOURCE_SPLIT_FAMILIES",
                "Rows": len(output),
                "UsableRows": len(usable),
                "ReconstructionFamilies": "SN_standardized_branch;BAO_standardized_branch",
                "SignStableRule": "public SN and BAO standardized branch signs agree",
                "PublicBranchStableRows": int(usable["PublicBranchSignStable"].sum()) if not usable.empty else 0,
                "PublicBranchOppositeRows": int(usable["PublicBranchOppositeSign"].sum()) if not usable.empty else 0,
                "TemplateStableRows": int(usable["TemplateSignStable"].sum()) if not usable.empty else 0,
                "CoordinateNative": True,
                "AllowedForK2Scoring": False,
                "Status": "PUBLIC_BRANCH_SIGN_FAMILY_PREFLIGHT_NOT_RECONSTRUCTION_FAMILY",
                "BlockingIssue": "reconstruction_families_missing;not_full_public_reconstruction_family",
                "NextAction": "Replace branch-sign preflight with public reconstruction-family export before K2/null scorecard.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
