#!/usr/bin/env python3
"""Build standardized source-split residual preflight rows.

This converts the joint SN/BAO preflight rows into dimensionless residual
coordinates by dividing each branch residual by its own diagonal uncertainty.
It is a common audit scale, not a physical K1 target and not K2 scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_joint_preflight.csv"
OUT = EVIDENCE / "source_split_standardized_preflight.csv"
SUMMARY = EVIDENCE / "source_split_standardized_preflight_summary.csv"


def safe_ratio(value, sigma) -> float:
    try:
        v = float(value)
        s = float(sigma)
    except (TypeError, ValueError):
        return float("nan")
    if not np.isfinite(v) or not np.isfinite(s) or s <= 0.0:
        return float("nan")
    return v / s


def main() -> None:
    df = pd.read_csv(SRC)
    rows = []
    for _, row in df.iterrows():
        sn_z = safe_ratio(row.get("SNCenteredResidualMu"), row.get("SNSigmaDiagProxy"))
        bao_z = safe_ratio(row.get("BAOLogResidualMean"), row.get("BAOSigmaDiagProxy"))
        contrast = sn_z - bao_z if np.isfinite(sn_z) and np.isfinite(bao_z) else np.nan
        rss = np.sqrt(sn_z * sn_z + bao_z * bao_z) if np.isfinite(sn_z) and np.isfinite(bao_z) else np.nan
        same_sign = bool(np.sign(sn_z) == np.sign(bao_z)) if np.isfinite(sn_z) and np.isfinite(bao_z) else False
        rows.append(
            {
                "TransformID": "T3_SOURCE_SPLIT_STANDARDIZED_PREFLIGHT",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_current": float(row["x_current"]),
                "SignStable": bool(row["SignStable"]),
                "HasSNAndBAO": bool(row["HasSNBin"]) and bool(row["HasBAOAnchor"]),
                "SNStandardizedResidual": sn_z,
                "BAOStandardizedResidual": bao_z,
                "StandardizedSNMinusBAO": contrast,
                "JointStandardizedRSS": rss,
                "SNBAOSameSign": same_sign,
                "ReadyForK2Scoring": False,
                "TransformStatus": "STANDARDIZED_SOURCE_SPLIT_PREFLIGHT_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "diagonal_standardization_only;coordinate_native_k1_missing;joint_covariance_missing",
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    complete = output[output["HasSNAndBAO"]]
    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_STANDARDIZED_PREFLIGHT",
                "Rows": len(output),
                "RowsWithSNAndBAO": len(complete),
                "RowsSameSign": int(complete["SNBAOSameSign"].sum()) if not complete.empty else 0,
                "RowsOppositeSign": int((~complete["SNBAOSameSign"]).sum()) if not complete.empty else 0,
                "MeanAbsStandardizedContrast": float(np.nanmean(np.abs(complete["StandardizedSNMinusBAO"])))
                if not complete.empty
                else np.nan,
                "MedianJointStandardizedRSS": float(np.nanmedian(complete["JointStandardizedRSS"]))
                if not complete.empty
                else np.nan,
                "MaxJointStandardizedRSS": float(np.nanmax(complete["JointStandardizedRSS"]))
                if not complete.empty
                else np.nan,
                "ReadyForK2Scoring": False,
                "Status": "PREFLIGHT_ONLY_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "diagonal_standardization_only;coordinate_native_k1_missing;joint_covariance_missing",
                "NextAction": "Replace diagonal standardization with a joint covariance and export coordinate-native K1.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
