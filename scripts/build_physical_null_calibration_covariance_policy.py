#!/usr/bin/env python3
"""Build covariance/uncertainty policy for physical-null calibration sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"

SOURCE_READINESS = EVIDENCE / "physical_null_calibration_source_readiness.csv"
MAPPING_READINESS = EVIDENCE / "physical_null_calibration_mapping_readiness.csv"

OUT = EVIDENCE / "physical_null_calibration_covariance_policy.csv"
OUT_READINESS = EVIDENCE / "physical_null_calibration_covariance_readiness.csv"


def truthy(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    source = pd.read_csv(SOURCE_READINESS).iloc[0]
    mapping = pd.read_csv(MAPPING_READINESS).iloc[0]

    rows = [
        {
            "CovariancePolicyID": "PHYSNULL_COV_SOURCE_NATIVE_V1",
            "PolicyRole": "preferred_measurement_route",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "CovarianceSource": "source-published covariance or uncertainty propagated to source-split rows",
            "CrossRowCorrelationRule": "use source-published correlation if available; otherwise declare diagonal uncertainty and mark weaker",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "SameScorecardTuningAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": True,
            "CurrentAvailable": False,
            "BlockingIssue": "source_covariance_not_ingested_or_propagated",
            "RequiredBeforeUse": "ingest source uncertainty/covariance and propagate it through the frozen mapping policy",
            "ClaimBoundary": "physical_null_covariance_policy_no_measurement_validation",
        },
        {
            "CovariancePolicyID": "PHYSNULL_COV_DECLARED_DIAGONAL_PROXY_V1",
            "PolicyRole": "preflight_sensitivity_only",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "CovarianceSource": "declared diagonal proxy from source uncertainty or conservative fractional width",
            "CrossRowCorrelationRule": "zero cross-correlation, reported as proxy only",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "SameScorecardTuningAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "source_uncertainty_not_available",
            "RequiredBeforeUse": "declare proxy uncertainty before scoring and report as sensitivity only",
            "ClaimBoundary": "physical_null_covariance_policy_no_measurement_validation",
        },
        {
            "CovariancePolicyID": "PHYSNULL_COV_REGISTERED_SHRINKAGE_PROXY_V1",
            "PolicyRole": "preflight_sensitivity_only",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "CovarianceSource": "source diagonal uncertainty plus predeclared shrinkage/correlation family",
            "CrossRowCorrelationRule": "predeclared lambda and correlation family; no tuning after scorecard",
            "ShrinkageAllowed": True,
            "BranchScatterAllowed": False,
            "SameScorecardTuningAllowed": False,
            "CanSupportPreflight": True,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "source_uncertainty_and_shrinkage_parameters_missing",
            "RequiredBeforeUse": "freeze lambda, correlation length, and source uncertainty before rerun",
            "ClaimBoundary": "physical_null_covariance_policy_no_measurement_validation",
        },
        {
            "CovariancePolicyID": "PHYSNULL_COV_FORBIDDEN_SCORECARD_RESCUE_V1",
            "PolicyRole": "forbidden",
            "AppliesTo": "BACKREACTION_ONLY;DYER_ROEDER_OPTICAL",
            "CovarianceSource": "uncertainty enlarged or selected after seeing K2 versus physical-null scores",
            "CrossRowCorrelationRule": "forbidden if selected to alter model ranking",
            "ShrinkageAllowed": False,
            "BranchScatterAllowed": False,
            "SameScorecardTuningAllowed": False,
            "CanSupportPreflight": False,
            "CanSupportMeasurementValidation": False,
            "CurrentAvailable": False,
            "BlockingIssue": "post_hoc_covariance_or_uncertainty_rescue_forbidden",
            "RequiredBeforeUse": "never allowed",
            "ClaimBoundary": "physical_null_covariance_policy_no_measurement_validation",
        },
    ]
    policy = pd.DataFrame(rows)
    policy.to_csv(OUT, index=False)

    measurement_available = bool(policy["CanSupportMeasurementValidation"].astype(bool).any()) and bool(
        policy[policy["CanSupportMeasurementValidation"].astype(bool)]["CurrentAvailable"].astype(bool).any()
    )
    readiness = pd.DataFrame(
        [
            {
                "ReadinessID": "PHYSICAL_NULL_CALIBRATION_COVARIANCE_READINESS",
                "PoliciesRegistered": int(len(policy)),
                "PreflightPoliciesRegistered": int(policy["CanSupportPreflight"].sum()),
                "MeasurementPoliciesRegistered": int(policy["CanSupportMeasurementValidation"].sum()),
                "CurrentlyAvailablePreflightPolicies": int(
                    (policy["CanSupportPreflight"] & policy["CurrentAvailable"]).sum()
                ),
                "CurrentlyAvailableMeasurementPolicies": int(
                    (policy["CanSupportMeasurementValidation"] & policy["CurrentAvailable"]).sum()
                ),
                "ForbiddenPoliciesRegistered": int(policy["PolicyRole"].eq("forbidden").sum()),
                "SourceReady": truthy(source["PhysicalNullCalibrationSourceReady"]),
                "MappingReady": truthy(mapping["PhysicalNullMappingReady"]),
                "PhysicalNullCovarianceReady": False,
                "PhysicalNullMeasurementReady": measurement_available,
                "PrimaryBlockingIssue": "source_covariance_not_ingested_or_propagated",
                "NextAction": "ingest source uncertainty/covariance, then propagate it through the frozen physical-null mapping policy",
                "Interpretation": "covariance policy is registered, but no physical-null source covariance is available yet",
                "ClaimBoundary": "physical_null_covariance_policy_no_measurement_validation",
            }
        ]
    )
    readiness.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
