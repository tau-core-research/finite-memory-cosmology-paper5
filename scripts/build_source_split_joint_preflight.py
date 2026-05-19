#!/usr/bin/env python3
"""Build a cautious SN+BAO source-split joint preflight table.

The output aligns the current diagnostic grid, binned Pantheon+ SN residuals,
and nearest DESI DR2 BAO residual anchors. The SN and BAO residuals are not put
on a final common physical scale here; the contrast columns are transform
development diagnostics only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

DIAGNOSTIC = EVIDENCE / "diagnostic_point_audit.csv"
SN_BINS = EVIDENCE / "sn_residual_binned_preflight.csv"
BAO_ROWS = EVIDENCE / "bao_residual_transform_preflight.csv"
OUT = EVIDENCE / "source_split_joint_preflight.csv"
SUMMARY = EVIDENCE / "source_split_joint_preflight_summary.csv"


def weighted_mean(values: np.ndarray, sigma: np.ndarray) -> tuple[float, float]:
    weights = np.where(sigma > 0.0, 1.0 / (sigma * sigma), 0.0)
    denom = float(np.sum(weights))
    if denom <= 0.0:
        return float("nan"), float("nan")
    return float(np.sum(weights * values) / denom), float(np.sqrt(1.0 / denom))


def nearest_bao_anchor(bao: pd.DataFrame, z: float) -> dict:
    dr2 = bao[bao["ProductID"].eq("DESI_DR2_BAO_ALL_GAUSSIAN")].copy()
    if dr2.empty:
        return {}
    distances = np.abs(dr2["z"].to_numpy(float) - float(z))
    nearest_distance = float(np.min(distances))
    group = dr2[distances == nearest_distance]
    mean, sigma = weighted_mean(
        group["LogResidual"].to_numpy(float),
        group["SigmaDiag"].to_numpy(float),
    )
    return {
        "BAONearestZ": float(group["z"].iloc[0]),
        "BAOAnchorRows": int(len(group)),
        "BAOLogResidualMean": mean,
        "BAOSigmaDiagProxy": sigma,
        "BAOAnchorDeltaZ": nearest_distance,
        "BAOQuantities": "|".join(sorted(set(group["Quantity"].astype(str)))),
    }


def main() -> None:
    diagnostic = pd.read_csv(DIAGNOSTIC)
    sn_bins = pd.read_csv(SN_BINS)
    bao = pd.read_csv(BAO_ROWS)

    rows = []
    for i, item in diagnostic.reset_index(drop=True).iterrows():
        z = float(item["z"])
        sn_match = sn_bins[sn_bins["z_grid"].round(8).eq(round(z, 8))]
        sn = sn_match.iloc[0].to_dict() if not sn_match.empty else {}
        bao_anchor = nearest_bao_anchor(bao, z)

        sn_value = float(sn.get("CenteredResidualMeanMu", np.nan))
        bao_value = float(bao_anchor.get("BAOLogResidualMean", np.nan))
        contrast = sn_value - bao_value if np.isfinite(sn_value) and np.isfinite(bao_value) else np.nan
        has_sn = bool(sn)
        has_bao = bool(bao_anchor)

        rows.append(
            {
                "TransformID": "T3_SN_BAO_JOINT_RECONSTRUCTION_PREFLIGHT",
                "GridIndex": int(i),
                "z_grid": z,
                "x_current": float(item["x"]),
                "SignStable": bool(item["sign_stable"]),
                "CurrentPacketDecision": item["decision"],
                "HasSNBin": has_sn,
                "SNRows": int(sn.get("Rows", 0)) if has_sn else 0,
                "SNCenteredResidualMu": sn_value,
                "SNSigmaDiagProxy": float(sn.get("SigmaDiagProxy", np.nan)),
                "HasBAOAnchor": has_bao,
                "BAONearestZ": bao_anchor.get("BAONearestZ", np.nan),
                "BAOAnchorRows": int(bao_anchor.get("BAOAnchorRows", 0)) if has_bao else 0,
                "BAOLogResidualMean": bao_value,
                "BAOSigmaDiagProxy": bao_anchor.get("BAOSigmaDiagProxy", np.nan),
                "BAOAnchorDeltaZ": bao_anchor.get("BAOAnchorDeltaZ", np.nan),
                "BAOQuantities": bao_anchor.get("BAOQuantities", ""),
                "UncalibratedSNMinusBAOContrast": contrast,
                "ReadyForK2Scoring": False,
                "TransformStatus": "SOURCE_SPLIT_PREFLIGHT_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "different_residual_units;coordinate_native_k1_missing;joint_covariance_missing",
                "ClaimBoundary": "preflight_only_no_measurement_validation",
            }
        )

    output = pd.DataFrame(rows)
    output.to_csv(OUT, index=False)

    complete = output[output["HasSNBin"] & output["HasBAOAnchor"]]
    summary = pd.DataFrame(
        [
            {
                "ArtifactID": "SOURCE_SPLIT_JOINT_PREFLIGHT",
                "Rows": len(output),
                "RowsWithSNAndBAO": len(complete),
                "SignStableRows": int(output["SignStable"].sum()),
                "SignUnstableRows": int((~output["SignStable"]).sum()),
                "MeanAbsUncalibratedContrast": float(np.nanmean(np.abs(output["UncalibratedSNMinusBAOContrast"]))),
                "MaxBAOAnchorDeltaZ": float(np.nanmax(output["BAOAnchorDeltaZ"])),
                "ReadyForK2Scoring": False,
                "Status": "PREFLIGHT_ONLY_NOT_MEASUREMENT_GATE",
                "BlockingIssue": "different_residual_units;coordinate_native_k1_missing;joint_covariance_missing",
                "NextAction": "Define a joint source-split residual scale, covariance, and coordinate-native K1 target.",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
