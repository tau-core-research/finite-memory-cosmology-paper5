#!/usr/bin/env python3
"""Build a coordinate-native source-split target preflight artifact.

This fulfills the first export task (TQ1) as a target-vector preflight. The
response coordinate is a standardized SN-minus-BAO branch contrast on a frozen
audit x_chi coordinate. It is not a K1 target and not K2 scoring.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
SRC = EVIDENCE / "source_split_standardized_preflight.csv"
OUT = EVIDENCE / "source_split_coordinate_native_target.csv"
SUMMARY = EVIDENCE / "source_split_coordinate_native_target_summary.csv"


def x_chi_normalized_local(z: np.ndarray, omega_m: float = 0.3, samples: int = 512) -> np.ndarray:
    """Local audit x_chi mapping to keep this script self-contained."""
    values = np.asarray(z, dtype=float)

    def integral_to(z_value: float) -> float:
        if z_value <= 0.0:
            return 0.0
        grid = np.linspace(0.0, z_value, int(samples))
        e_z = np.sqrt(float(omega_m) * (1.0 + grid) ** 3 + (1.0 - float(omega_m)))
        return float(np.trapezoid(1.0 / e_z, grid))

    chi = np.array([integral_to(float(item)) for item in values], dtype=float)
    return chi / float(np.max(chi))


def main() -> None:
    df = pd.read_csv(SRC)
    z = df["z_grid"].to_numpy(float)
    x_chi = x_chi_normalized_local(z)
    x_z = z / float(np.max(z))

    rows = []
    for i, row in df.reset_index(drop=True).iterrows():
        has_both = bool(row["HasSNAndBAO"])
        response = row["StandardizedSNMinusBAO"] if has_both and pd.notna(row["StandardizedSNMinusBAO"]) else np.nan
        rows.append(
            {
                "TargetID": "SS_TARGET_COORDINATE_NATIVE_V1",
                "GridIndex": int(row["GridIndex"]),
                "z_grid": float(row["z_grid"]),
                "x_coordinate": float(x_chi[i]),
                "x_mapping": "x_chi_normalized_flat_lcdm_audit",
                "x_z_normalized": float(x_z[i]),
                "SourceSplitResponse": response,
                "ResponseDefinition": "SN_standardized_minus_BAO_standardized",
                "HasSNAndBAO": has_both,
                "SNStandardizedResidual": row["SNStandardizedResidual"],
                "BAOStandardizedResidual": row["BAOStandardizedResidual"],
                "SignStableTemplate": bool(row["SignStable"]),
                "SNBAOSameSign": bool(row["SNBAOSameSign"]),
                "CoordinateNative": True,
                "ReadyForK2Scoring": False,
                "TransformStatus": "COORDINATE_NATIVE_TARGET_PREFLIGHT_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "k1_target_missing;joint_covariance_missing;public_sign_family_missing",
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    usable = output[output["HasSNAndBAO"] & output["SourceSplitResponse"].notna()]
    summary = pd.DataFrame(
        [
            {
                "TargetID": "SS_TARGET_COORDINATE_NATIVE_V1",
                "Rows": len(output),
                "UsableRows": len(usable),
                "XMapping": "x_chi_normalized_flat_lcdm_audit",
                "ResponseDefinition": "SN_standardized_minus_BAO_standardized",
                "MeanAbsResponse": float(np.nanmean(np.abs(usable["SourceSplitResponse"]))) if not usable.empty else np.nan,
                "SignStableUsableRows": int(usable["SignStableTemplate"].sum()) if not usable.empty else 0,
                "OppositeSignUsableRows": int((~usable["SNBAOSameSign"]).sum()) if not usable.empty else 0,
                "CoordinateNative": True,
                "ReadyForK2Scoring": False,
                "Status": "PREFLIGHT_TARGET_EXPORTED",
                "BlockingIssue": "k1_target_missing;joint_covariance_missing;public_sign_family_missing",
                "NextAction": "Export coordinate-native K1 target, joint covariance, and public sign-family table.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
