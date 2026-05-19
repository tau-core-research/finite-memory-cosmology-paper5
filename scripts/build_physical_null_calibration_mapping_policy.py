#!/usr/bin/env python3
"""Build mapping policy for future physical-null calibration sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

SOURCE_REGISTRY = EVIDENCE / "physical_null_calibration_source_registry.csv"
TARGET = EVIDENCE / "source_split_coordinate_native_target.csv"

OUT = EVIDENCE / "physical_null_calibration_mapping_policy.csv"
OUT_READINESS = EVIDENCE / "physical_null_calibration_mapping_readiness.csv"


def main() -> None:
    sources = pd.read_csv(SOURCE_REGISTRY)
    target = pd.read_csv(TARGET)
    usable = target[target["HasSNAndBAO"].astype(str).str.lower().eq("true")].copy()
    x_min = float(usable["x_coordinate"].min())
    x_max = float(usable["x_coordinate"].max())
    z_min = float(usable["z_grid"].min())
    z_max = float(usable["z_grid"].max())

    candidate_sources = sources[sources["SourceClass"].ne("forbidden_post_hoc_fit")]
    rows = []
    for _, row in candidate_sources.iterrows():
        rows.append(
            {
                "MappingPolicyID": f"MAP_{row['SourceID']}",
                "SourceID": row["SourceID"],
                "NullID": row["NullID"],
                "TargetVector": "SS_TARGET_COORDINATE_NATIVE_V1",
                "TargetRows": int(len(usable)),
                "TargetZMin": z_min,
                "TargetZMax": z_max,
                "TargetXMin": x_min,
                "TargetXMax": x_max,
                "CoordinateBasis": "source_split_x_coordinate",
                "AllowedMapping": "monotone interpolation in source redshift or declared x-coordinate, then projection to target GridIndex rows",
                "AllowedExtrapolation": False,
                "AllowedSmoothing": "source-published smoothing only; no smoothing selected from K2 residuals",
                "NormalizationRule": "preserve externally calibrated amplitude; unit-norm only for preflight templates",
                "SameScorecardTuningAllowed": False,
                "RequiresSourceData": True,
                "RequiresSourceCovariance": bool(row["RequiresCovariance"]),
                "MappingImplemented": False,
                "AllowedForPreflightCalibration": False,
                "AllowedForMeasurementCalibration": False,
                "BlockingIssue": "source_data_not_ingested;mapping_not_executed",
                "NextAction": "ingest source table, validate redshift/x coverage, then export row-aligned mapped amplitude with uncertainty",
                "ClaimBoundary": "physical_null_mapping_policy_no_measurement_validation",
            }
        )

    policy = pd.DataFrame(rows)
    policy.to_csv(OUT, index=False)

    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_CALIBRATION_MAPPING_READINESS",
                "MappingPoliciesRegistered": int(len(policy)),
                "TargetRows": int(len(usable)),
                "TargetZRange": f"{z_min}..{z_max}",
                "TargetXRange": f"{x_min}..{x_max}",
                "MappingsImplemented": int(policy["MappingImplemented"].sum()),
                "PreflightCalibrationMappingsAllowed": int(policy["AllowedForPreflightCalibration"].sum()),
                "MeasurementCalibrationMappingsAllowed": int(policy["AllowedForMeasurementCalibration"].sum()),
                "SameScorecardTuningAllowed": False,
                "PhysicalNullMappingReady": False,
                "PrimaryBlockingIssue": "source_data_not_ingested;mapping_not_executed",
                "NextAction": "ingest physical-null calibration source tables before executing mapping policy",
                "Interpretation": "mapping policy is frozen, but no physical-null calibration source is mapped yet",
                "ClaimBoundary": "physical_null_mapping_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
