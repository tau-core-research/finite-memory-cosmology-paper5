#!/usr/bin/env python3
"""Build a compact dashboard for the physical-null calibration branch."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

HIERARCHY = EVIDENCE / "physical_null_hierarchy_readiness.csv"
AMPLITUDE = EVIDENCE / "physical_null_amplitude_policy_readiness.csv"
PREFLIGHT = EVIDENCE / "physical_null_preflight_summary.csv"
ROW_AUDIT = EVIDENCE / "physical_null_preflight_row_summary.csv"
SOURCE = EVIDENCE / "physical_null_calibration_source_readiness.csv"
MAPPING = EVIDENCE / "physical_null_calibration_mapping_readiness.csv"
COVARIANCE = EVIDENCE / "physical_null_calibration_covariance_readiness.csv"

OUT = EVIDENCE / "physical_null_readiness_dashboard.csv"
OUT_SUMMARY = EVIDENCE / "physical_null_readiness_summary.csv"


def read_first(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"{path} is empty")
    return df.iloc[0]


def bool_value(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    hierarchy = read_first(HIERARCHY)
    amplitude = read_first(AMPLITUDE)
    preflight = read_first(PREFLIGHT)
    row_audit = read_first(ROW_AUDIT)
    source = read_first(SOURCE)
    mapping = read_first(MAPPING)
    covariance = read_first(COVARIANCE)

    rows = [
        {
            "GateID": "PN_G1_HIERARCHY_REGISTERED",
            "GateName": "physical null hierarchy",
            "Status": "READY_PREFLIGHT",
            "Ready": True,
            "BlocksMeasurement": False,
            "KeyMetric": f"registered_nulls={hierarchy['RegisteredNulls']}",
            "BlockingIssue": hierarchy["PrimaryBlockingIssue"],
            "NextAction": hierarchy["NextAction"],
        },
        {
            "GateID": "PN_G2_AMPLITUDE_POLICY",
            "GateName": "amplitude policy",
            "Status": "READY_PREFLIGHT_ONLY",
            "Ready": bool_value(amplitude["ScoringPreflightAllowed"]),
            "BlocksMeasurement": True,
            "KeyMetric": f"measurement_validation_allowed={amplitude['MeasurementValidationAllowed']}",
            "BlockingIssue": amplitude["PrimaryBlockingIssue"],
            "NextAction": amplitude["NextAction"],
        },
        {
            "GateID": "PN_G3_PREFLIGHT_SCORECARD",
            "GateName": "physical null preflight scorecard",
            "Status": "SUPPORTIVE_BUT_NARROW_PREFLIGHT",
            "Ready": True,
            "BlocksMeasurement": True,
            "KeyMetric": (
                f"delta_aic_k2_minus_best_physical={preflight['DeltaAIC_K2_minus_BestPhysicalNull']}"
            ),
            "BlockingIssue": preflight["PrimaryBlockingIssue"],
            "NextAction": "keep as preflight evidence; do not promote until source calibration exists",
        },
        {
            "GateID": "PN_G4_ROW_AUDIT",
            "GateName": "row-level physical null audit",
            "Status": "SUPPORTIVE_BUT_SPLIT",
            "Ready": True,
            "BlocksMeasurement": True,
            "KeyMetric": (
                f"k2_vs_best_physical_rows={row_audit['RowsWhereK2BeatsBestPhysicalNull']}/"
                f"{row_audit['Rows']}"
            ),
            "BlockingIssue": "physical_nulls_competitive_on_half_rows",
            "NextAction": "calibrate physical-null amplitudes independently before stronger comparison",
        },
        {
            "GateID": "PN_G5_SOURCE_INGESTION",
            "GateName": "calibration source ingestion",
            "Status": "BLOCKED",
            "Ready": bool_value(source["PhysicalNullCalibrationSourceReady"]),
            "BlocksMeasurement": True,
            "KeyMetric": f"sources_available_in_repo={source['SourcesAvailableInRepo']}",
            "BlockingIssue": source["PrimaryBlockingIssue"],
            "NextAction": source["NextAction"],
        },
        {
            "GateID": "PN_G6_MAPPING_EXECUTION",
            "GateName": "source-to-target mapping",
            "Status": "POLICY_READY_EXECUTION_BLOCKED",
            "Ready": bool_value(mapping["PhysicalNullMappingReady"]),
            "BlocksMeasurement": True,
            "KeyMetric": f"mappings_implemented={mapping['MappingsImplemented']}",
            "BlockingIssue": mapping["PrimaryBlockingIssue"],
            "NextAction": mapping["NextAction"],
        },
        {
            "GateID": "PN_G7_COVARIANCE_PROPAGATION",
            "GateName": "physical-null covariance propagation",
            "Status": "POLICY_READY_EXECUTION_BLOCKED",
            "Ready": bool_value(covariance["PhysicalNullCovarianceReady"]),
            "BlocksMeasurement": True,
            "KeyMetric": (
                f"available_measurement_policies={covariance['CurrentlyAvailableMeasurementPolicies']}"
            ),
            "BlockingIssue": covariance["PrimaryBlockingIssue"],
            "NextAction": covariance["NextAction"],
        },
    ]
    dashboard = pd.DataFrame(rows)
    dashboard["ClaimBoundary"] = "physical_null_dashboard_no_measurement_validation"
    dashboard.to_csv(OUT, index=False)

    measurement_ready = bool(
        bool_value(source["PhysicalNullCalibrationSourceReady"])
        and bool_value(mapping["PhysicalNullMappingReady"])
        and bool_value(covariance["PhysicalNullCovarianceReady"])
        and bool_value(covariance["PhysicalNullMeasurementReady"])
    )
    blockers = dashboard[dashboard["BlocksMeasurement"].astype(bool) & ~dashboard["Ready"].astype(bool)]
    summary = pd.DataFrame(
        [
            {
                "SummaryID": "PHYSICAL_NULL_READINESS_DASHBOARD_SUMMARY",
                "Gates": len(dashboard),
                "ReadyGates": int(dashboard["Ready"].sum()),
                "MeasurementBlockingGates": int(dashboard["BlocksMeasurement"].sum()),
                "OpenMeasurementBlockers": int(len(blockers)),
                "K2PreflightStatus": "supportive_but_narrow",
                "PhysicalNullMeasurementReady": measurement_ready,
                "PrimaryBlockingIssue": "source_ingestion_mapping_and_covariance_missing",
                "NextAction": "ingest physical-null calibration sources, execute mapping policy, and propagate covariance before measurement comparison",
                "Interpretation": "physical-null branch has useful K2-supportive preflight evidence but remains blocked for measurement validation",
                "ClaimBoundary": "physical_null_dashboard_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
