#!/usr/bin/env python3
"""Build source registry for external nonzero source-split K1 targets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
REGISTRY_OUT = EVIDENCE / "source_split_external_k1_source_registry.csv"
READINESS_OUT = EVIDENCE / "source_split_external_k1_source_readiness.csv"


def registry_rows() -> list[dict[str, object]]:
    return [
        {
            "K1SourceID": "K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE",
            "SourceClass": "likelihood_native_baseline",
            "Status": "planned",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": True,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "likelihood_native_baseline_not_exported",
            "RequiredArtifact": "data/k1/source_split_external_k1_response.csv",
            "NextAction": "Export a likelihood-native joint SN+BAO no-memory baseline with frozen parameters and covariance.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_EXTERNAL_RECONSTRUCTION_FAMILY_MEAN",
            "SourceClass": "external_reconstruction_family_mean",
            "Status": "candidate_path_declared",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "external_family_mean_policy_not_predeclared;independence_policy_not_declared",
            "RequiredArtifact": "data/k1/source_split_external_k1_response.csv",
            "NextAction": "Declare a family-mean K1 policy before scoring; do not choose amplitude from K2 residuals.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_INDEPENDENT_PUBLIC_MODEL_RESPONSE",
            "SourceClass": "independent_public_model_response",
            "Status": "planned",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "independent_public_model_not_selected",
            "RequiredArtifact": "data/k1/source_split_external_k1_response.csv",
            "NextAction": "Select an independent public model response and freeze its amplitude policy before K2 scoring.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_EXTERNAL_PUBLIC_RESPONSE_OPERATOR",
            "SourceClass": "external_public_response_operator",
            "Status": "planned",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "operator_not_specified;amplitude_policy_not_declared",
            "RequiredArtifact": "data/k1/source_split_external_k1_response.csv",
            "NextAction": "Specify the public response operator and freeze normalization before looking at K2 improvement.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_CURRENT_ZERO_CONTRAST_CONTROL",
            "SourceClass": "fair_null_control",
            "Status": "available_control",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": False,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "zero_response_degenerate_for_multiplicative_k2",
            "RequiredArtifact": "evidence/source_split_k1_coordinate_native_target.csv",
            "NextAction": "Keep as no-memory null comparator, not primary external K1.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_SINGLE_BRANCH_RESPONSE_CONTROL",
            "SourceClass": "diagnostic_control",
            "Status": "available_control",
            "UsesPublicSN": False,
            "UsesPublicBAO": False,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": False,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": False,
            "FittedInThisNote": False,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "single_branch_control_not_source_split_k1",
            "RequiredArtifact": "evidence/source_split_k1_response_candidate_audit.csv",
            "NextAction": "Keep SN/BAO branch responses as diagnostic controls only.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
        {
            "K1SourceID": "K1SRC_SAME_DATA_AMPLITUDE_RESCUE",
            "SourceClass": "forbidden_rescue_path",
            "Status": "forbidden",
            "UsesPublicSN": True,
            "UsesPublicBAO": True,
            "CoordinateNative": True,
            "LikelihoodNative": False,
            "UsesJointCovariance": True,
            "CanProduceNonzeroK1": True,
            "SameDataAmplitudeFit": True,
            "FittedInThisNote": True,
            "AllowedForExternalK1Export": False,
            "BlockingIssue": "same_data_amplitude_fit;fitted_in_this_note;post_hoc_k1_rescue",
            "RequiredArtifact": "",
            "NextAction": "Do not use this path.",
            "ClaimBoundary": "source_registry_only_no_measurement_validation",
        },
    ]


def readiness_rows(registry: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for _, row in registry.iterrows():
        allowed = bool(row["AllowedForExternalK1Export"]) and not str(row["BlockingIssue"]).strip()
        rows.append(
            {
                "K1SourceID": row["K1SourceID"],
                "SourceClass": row["SourceClass"],
                "Status": row["Status"],
                "AllowedForExternalK1Export": allowed,
                "CanProduceNonzeroK1": row["CanProduceNonzeroK1"],
                "BlockingIssue": row["BlockingIssue"],
                "RequiredArtifact": row["RequiredArtifact"],
                "NextAction": row["NextAction"],
                "ClaimBoundary": row["ClaimBoundary"],
            }
        )
    return rows


def main() -> None:
    registry = pd.DataFrame(registry_rows())
    registry.to_csv(REGISTRY_OUT, index=False)
    readiness = pd.DataFrame(readiness_rows(registry))
    readiness.to_csv(READINESS_OUT, index=False)
    print(f"Wrote {REGISTRY_OUT}")
    print(f"Wrote {READINESS_OUT}")


if __name__ == "__main__":
    main()
