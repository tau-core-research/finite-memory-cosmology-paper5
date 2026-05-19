#!/usr/bin/env python3
"""Register candidate sources for physical-null amplitude calibration.

This is a source/readiness registry only. It does not download data, calibrate
amplitudes, or promote any physical null to measurement status.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

REGISTRY = EVIDENCE / "physical_null_calibration_source_registry.csv"
READINESS = EVIDENCE / "physical_null_calibration_source_readiness.csv"
TASKS = EVIDENCE / "physical_null_calibration_task_queue.csv"


def main() -> None:
    rows = [
        {
            "SourceID": "BACKREACTION_EXTENDED_REDSHIFT_CONSTRAINTS",
            "NullID": "BACKREACTION_ONLY",
            "SourceClass": "published_backreaction_constraint",
            "CandidateDescription": "Published observational constraints on cosmic backreaction over an extended redshift range.",
            "CouldSetAmplitude": True,
            "RequiresDigitizationOrTable": True,
            "RequiresCoordinateMapping": True,
            "RequiresCovariance": True,
            "AvailableInRepo": False,
            "AllowedForPreflightCalibration": False,
            "AllowedForMeasurementCalibration": False,
            "BlockingIssue": "public_table_or_machine_readable_constraint_not_ingested;source_split_mapping_missing;covariance_missing",
            "NextAction": "locate machine-readable table or reproduce published backreaction envelope, then map to source-split vector before scoring",
            "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "BACKREACTION_SIMULATION_PRIOR",
            "NullID": "BACKREACTION_ONLY",
            "SourceClass": "independent_simulation_prior",
            "CandidateDescription": "Independent simulation or averaging prior for backreaction amplitude, frozen before K2 score inspection.",
            "CouldSetAmplitude": True,
            "RequiresDigitizationOrTable": False,
            "RequiresCoordinateMapping": True,
            "RequiresCovariance": True,
            "AvailableInRepo": False,
            "AllowedForPreflightCalibration": False,
            "AllowedForMeasurementCalibration": False,
            "BlockingIssue": "independent_simulation_prior_not_defined;covariance_or_prior_width_missing",
            "NextAction": "define an external simulation-prior amplitude and uncertainty without using the tested scorecard residuals",
            "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "DYER_ROEDER_ALPHA_Z_CONSTRAINTS",
            "NullID": "DYER_ROEDER_OPTICAL",
            "SourceClass": "published_optical_clumpiness_constraint",
            "CandidateDescription": "Published Dyer-Roeder alpha(z), optical clumpiness, opacity, or lensing constraint.",
            "CouldSetAmplitude": True,
            "RequiresDigitizationOrTable": True,
            "RequiresCoordinateMapping": True,
            "RequiresCovariance": True,
            "AvailableInRepo": False,
            "AllowedForPreflightCalibration": False,
            "AllowedForMeasurementCalibration": False,
            "BlockingIssue": "public_alpha_or_clumpiness_table_not_ingested;source_split_mapping_missing;covariance_missing",
            "NextAction": "identify an alpha(z)/clumpiness/lensing constraint with covariance and map it to the source-split vector",
            "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "OPTICAL_LENSING_OR_OPACITY_PROXY",
            "NullID": "DYER_ROEDER_OPTICAL",
            "SourceClass": "public_optical_proxy",
            "CandidateDescription": "Weak-lensing, opacity, or foreground visibility proxy that can bound optical-propagation amplitude.",
            "CouldSetAmplitude": True,
            "RequiresDigitizationOrTable": True,
            "RequiresCoordinateMapping": True,
            "RequiresCovariance": True,
            "AvailableInRepo": False,
            "AllowedForPreflightCalibration": False,
            "AllowedForMeasurementCalibration": False,
            "BlockingIssue": "proxy_not_selected;mapping_to_dyer_roeder_template_not_declared;covariance_missing",
            "NextAction": "select public optical proxy and predeclare transform into Dyer-Roeder template amplitude before scoring",
            "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
        },
        {
            "SourceID": "SAME_SCORECARD_PHYSICAL_NULL_AMPLITUDE",
            "NullID": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "SourceClass": "forbidden_post_hoc_fit",
            "CandidateDescription": "Amplitude chosen by least squares, AIC/BIC, or row residuals on the same physical-null scorecard.",
            "CouldSetAmplitude": False,
            "RequiresDigitizationOrTable": False,
            "RequiresCoordinateMapping": False,
            "RequiresCovariance": False,
            "AvailableInRepo": False,
            "AllowedForPreflightCalibration": False,
            "AllowedForMeasurementCalibration": False,
            "BlockingIssue": "post_hoc_same_scorecard_amplitude_fit_forbidden",
            "NextAction": "do not use this source route",
            "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
        },
    ]
    registry = pd.DataFrame(rows)
    registry.to_csv(REGISTRY, index=False)

    candidate = registry[registry["SourceClass"].ne("forbidden_post_hoc_fit")]
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_CALIBRATION_SOURCE_READINESS",
                "CandidateSourcesRegistered": int(len(candidate)),
                "SourcesAvailableInRepo": int(candidate["AvailableInRepo"].sum()),
                "PreflightCalibrationSourcesAllowed": int(candidate["AllowedForPreflightCalibration"].sum()),
                "MeasurementCalibrationSourcesAllowed": int(candidate["AllowedForMeasurementCalibration"].sum()),
                "ForbiddenRoutesRegistered": int(registry["SourceClass"].eq("forbidden_post_hoc_fit").sum()),
                "BackreactionCandidateSources": int(candidate["NullID"].eq("BACKREACTION_ONLY").sum()),
                "OpticalCandidateSources": int(candidate["NullID"].eq("DYER_ROEDER_OPTICAL").sum()),
                "PhysicalNullCalibrationSourceReady": False,
                "PrimaryBlockingIssue": "candidate_sources_registered_but_not_ingested_or_mapped",
                "NextAction": "obtain one backreaction and one optical calibration source with covariance, then map to source-split vector before rerun",
                "Interpretation": "calibration source classes are registered, but no source is available for measurement-grade physical-null amplitudes",
                "ClaimBoundary": "physical_null_calibration_source_registry_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(READINESS, index=False)

    tasks = pd.DataFrame(
        [
            {
                "TaskID": "PHYSNULL_SRC_1_BACKREACTION_TABLE",
                "Priority": 1,
                "NullID": "BACKREACTION_ONLY",
                "Task": "Find or reproduce a public backreaction constraint/envelope table over redshift.",
                "RequiredOutput": "data/physical_nulls/backreaction_calibration_source.csv",
                "BlocksMeasurementValidation": True,
                "Status": "PENDING",
            },
            {
                "TaskID": "PHYSNULL_SRC_2_OPTICAL_ALPHA_TABLE",
                "Priority": 2,
                "NullID": "DYER_ROEDER_OPTICAL",
                "Task": "Find a public Dyer-Roeder alpha(z), clumpiness, lensing, or opacity constraint with uncertainty.",
                "RequiredOutput": "data/physical_nulls/dyer_roeder_optical_calibration_source.csv",
                "BlocksMeasurementValidation": True,
                "Status": "PENDING",
            },
            {
                "TaskID": "PHYSNULL_SRC_3_SOURCE_SPLIT_MAPPING",
                "Priority": 3,
                "NullID": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
                "Task": "Predeclare mapping from each physical-null source into the source-split coordinate vector.",
                "RequiredOutput": "evidence/physical_null_calibration_mapping_policy.csv",
                "BlocksMeasurementValidation": True,
                "Status": "PENDING",
            },
            {
                "TaskID": "PHYSNULL_SRC_4_COVARIANCE_POLICY",
                "Priority": 4,
                "NullID": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
                "Task": "Attach covariance or uncertainty propagation for each calibrated physical-null amplitude.",
                "RequiredOutput": "evidence/physical_null_calibration_covariance_policy.csv",
                "BlocksMeasurementValidation": True,
                "Status": "PENDING",
            },
        ]
    )
    tasks.to_csv(TASKS, index=False)

    print(f"Wrote {REGISTRY}")
    print(f"Wrote {READINESS}")
    print(f"Wrote {TASKS}")


if __name__ == "__main__":
    main()
