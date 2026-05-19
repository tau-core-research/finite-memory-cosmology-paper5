#!/usr/bin/env python3
"""Build the coordinate-native source-split K1/no-memory control target.

This fulfills the second source-split export task (TQ2) as a conservative
no-memory control artifact. The exported response is not fit to K2 residuals
and is not authorized for K2 scoring until joint covariance and public
sign-family exports exist.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_coordinate_native_target.csv"
OUT = EVIDENCE / "source_split_k1_coordinate_native_target.csv"
SUMMARY = EVIDENCE / "source_split_k1_coordinate_native_target_summary.csv"


def main() -> None:
    df = pd.read_csv(SRC)
    rows = []
    for _, row in df.iterrows():
        has_target = bool(row["HasSNAndBAO"]) and pd.notna(row["SourceSplitResponse"])
        rows.append(
            {
                "K1TargetID": "SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET",
                "SourceTargetID": row["TargetID"],
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(row["x_coordinate"]),
                "x_mapping": row["x_mapping"],
                "K1NoMemoryResponse": 0.0 if has_target else np.nan,
                "NoMemoryDefinition": "zero_source_split_branch_contrast",
                "SourceSplitResponse": row["SourceSplitResponse"],
                "HasTargetRow": has_target,
                "CoordinateNative": True,
                "UsesPublicSN": True,
                "UsesPublicBAO": True,
                "UsesJointCovariance": False,
                "AmplitudePolicy": "zero branch contrast; no amplitude fit",
                "SameDataAmplitudeFit": False,
                "SignFamilyExported": False,
                "AllowedForK2Scoring": False,
                "TargetStatus": "K1_CONTROL_EXPORTED_NOT_SCORING_TARGET",
                "BlockingIssue": "joint_covariance_missing;public_sign_family_missing",
                "ClaimBoundary": "no_memory_control_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    usable = output[output["HasTargetRow"] & output["K1NoMemoryResponse"].notna()]
    target = df[df["HasSNAndBAO"] & df["SourceSplitResponse"].notna()]
    summary = pd.DataFrame(
        [
            {
                "K1TargetID": "SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET",
                "Rows": len(output),
                "UsableRows": len(usable),
                "XMapping": "x_chi_normalized_flat_lcdm_audit",
                "NoMemoryDefinition": "zero_source_split_branch_contrast",
                "MeanK1NoMemoryResponse": float(np.nanmean(usable["K1NoMemoryResponse"])) if not usable.empty else np.nan,
                "MeanAbsSourceSplitResponse": float(np.nanmean(np.abs(target["SourceSplitResponse"]))) if not target.empty else np.nan,
                "CoordinateNative": True,
                "UsesJointCovariance": False,
                "SignFamilyExported": False,
                "AllowedForK2Scoring": False,
                "Status": "K1_CONTROL_EXPORTED_NOT_SCORING_TARGET",
                "BlockingIssue": "joint_covariance_missing;public_sign_family_missing",
                "NextAction": "Export public sign-family and joint covariance before any K2/null scoring.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
