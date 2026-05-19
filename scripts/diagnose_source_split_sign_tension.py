#!/usr/bin/env python3
"""Diagnose sign tension in the standardized source-split preflight."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_standardized_preflight.csv"
OUT = EVIDENCE / "source_split_sign_tension_audit.csv"
SUMMARY = EVIDENCE / "source_split_sign_tension_summary.csv"


def sign_label(value) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "missing"
    if not np.isfinite(v):
        return "missing"
    if v > 0.0:
        return "positive"
    if v < 0.0:
        return "negative"
    return "zero"


def tension_type(row: pd.Series) -> str:
    if not bool(row["HasSNAndBAO"]):
        return "MISSING_BRANCH"
    sn = sign_label(row["SNStandardizedResidual"])
    bao = sign_label(row["BAOStandardizedResidual"])
    if sn == "missing" or bao == "missing":
        return "MISSING_BRANCH"
    if sn == bao:
        return "SOURCE_SPLIT_ALIGNED_SIGN_STABLE" if bool(row["SignStable"]) else "SOURCE_SPLIT_ALIGNED_SIGN_UNSTABLE"
    return "SOURCE_SPLIT_CONTRAST_SIGN_STABLE" if bool(row["SignStable"]) else "SOURCE_SPLIT_CONTRAST_SIGN_UNSTABLE"


def main() -> None:
    df = pd.read_csv(SRC)
    rows = []
    for _, row in df.iterrows():
        sn = float(row["SNStandardizedResidual"]) if pd.notna(row["SNStandardizedResidual"]) else np.nan
        bao = float(row["BAOStandardizedResidual"]) if pd.notna(row["BAOStandardizedResidual"]) else np.nan
        contrast = float(row["StandardizedSNMinusBAO"]) if pd.notna(row["StandardizedSNMinusBAO"]) else np.nan
        dominant = "missing"
        if np.isfinite(sn) and np.isfinite(bao):
            dominant = "SN" if abs(sn) > abs(bao) else "BAO"
        rows.append(
            {
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_current": float(row["x_current"]),
                "SignStable": bool(row["SignStable"]),
                "HasSNAndBAO": bool(row["HasSNAndBAO"]),
                "SNStandardizedResidual": sn,
                "BAOStandardizedResidual": bao,
                "SNSign": sign_label(sn),
                "BAOSign": sign_label(bao),
                "SNBAOSameSign": bool(row["SNBAOSameSign"]),
                "AbsStandardizedContrast": abs(contrast) if np.isfinite(contrast) else np.nan,
                "JointStandardizedRSS": row["JointStandardizedRSS"],
                "DominantBranchByAbsResidual": dominant,
                "TensionType": tension_type(row),
                "ReadyForK2Scoring": False,
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT, index=False)

    complete = audit[audit["HasSNAndBAO"]]
    sign_stable = complete[complete["SignStable"]]
    sign_unstable = complete[~complete["SignStable"]]
    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_SIGN_TENSION_AUDIT",
                "Rows": len(audit),
                "RowsWithSNAndBAO": len(complete),
                "SignStableRowsWithSNAndBAO": len(sign_stable),
                "SignStableOppositeSignRows": int((~sign_stable["SNBAOSameSign"]).sum()),
                "SignUnstableRowsWithSNAndBAO": len(sign_unstable),
                "SignUnstableOppositeSignRows": int((~sign_unstable["SNBAOSameSign"]).sum()),
                "MeanAbsContrastSignStable": float(sign_stable["AbsStandardizedContrast"].mean()) if not sign_stable.empty else np.nan,
                "MeanAbsContrastSignUnstable": float(sign_unstable["AbsStandardizedContrast"].mean()) if not sign_unstable.empty else np.nan,
                "DominantBranchCounts": "|".join(
                    f"{key}:{value}" for key, value in complete["DominantBranchByAbsResidual"].value_counts().to_dict().items()
                ),
                "Status": "PREFLIGHT_SOURCE_SPLIT_WARNING",
                "BlockingIssue": "diagonal_standardization_only;coordinate_native_k1_missing;joint_covariance_missing",
                "NextAction": "Build joint covariance and coordinate-native K1 before using sign tension for K2 scoring.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
