#!/usr/bin/env python3
"""Build candidate plan for public source-split reconstruction-family exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "source_split_reconstruction_family_candidate_plan.csv"
SUMMARY = EVIDENCE / "source_split_reconstruction_family_candidate_summary.csv"


CANDIDATES = [
    {
        "CandidateFamilyID": "RFAM_SN_RESIDUAL_BRANCH",
        "FamilyType": "SN_branch",
        "SourceProducts": "PANTHEON_PLUS_SH0ES_SN",
        "UsesPublicSN": True,
        "UsesPublicBAO": False,
        "CoordinateNativeTarget": True,
        "ResponseExportPath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "CurrentArtifact": "evidence/sn_residual_binned_preflight.csv",
        "CurrentStatus": "PREFLIGHT_AVAILABLE_NOT_FAMILY_EXPORT",
        "RequiredTransform": "map binned SN residuals to source-split response rows",
        "RequiredCovariance": "joint source-split covariance or declared shrinkage covariance",
        "AllowedRole": "candidate_family_input",
        "AllowedForK2ScoringNow": False,
        "BlockingIssue": "not_exported_in_reconstruction_family_schema;no_family_level_rule",
        "NextAction": "Export this branch in the long-format reconstruction-family schema.",
    },
    {
        "CandidateFamilyID": "RFAM_BAO_RESIDUAL_BRANCH",
        "FamilyType": "BAO_branch",
        "SourceProducts": "DESI_DR2_BAO_ALL_GAUSSIAN",
        "UsesPublicSN": False,
        "UsesPublicBAO": True,
        "CoordinateNativeTarget": True,
        "ResponseExportPath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "CurrentArtifact": "evidence/bao_residual_transform_preflight.csv",
        "CurrentStatus": "PREFLIGHT_AVAILABLE_NOT_FAMILY_EXPORT",
        "RequiredTransform": "map BAO residuals to source-split response rows",
        "RequiredCovariance": "joint source-split covariance or declared shrinkage covariance",
        "AllowedRole": "candidate_family_input",
        "AllowedForK2ScoringNow": False,
        "BlockingIssue": "not_exported_in_reconstruction_family_schema;no_family_level_rule",
        "NextAction": "Export this branch in the long-format reconstruction-family schema.",
    },
    {
        "CandidateFamilyID": "RFAM_SN_BAO_JOINT_SHRINKAGE",
        "FamilyType": "joint_reconstruction",
        "SourceProducts": "PANTHEON_PLUS_SH0ES_SN;DESI_DR2_BAO_ALL_GAUSSIAN",
        "UsesPublicSN": True,
        "UsesPublicBAO": True,
        "CoordinateNativeTarget": True,
        "ResponseExportPath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "CurrentArtifact": "evidence/source_split_joint_covariance_policy.csv",
        "CurrentStatus": "COVARIANCE_POLICY_AVAILABLE_NOT_PUBLIC_FULL_COVARIANCE",
        "RequiredTransform": "derive joint family response on the coordinate-native source-split target rows",
        "RequiredCovariance": "declared shrinkage covariance at minimum; public full covariance preferred",
        "AllowedRole": "candidate_joint_family",
        "AllowedForK2ScoringNow": False,
        "BlockingIssue": "joint_family_response_not_exported;public_full_covariance_missing",
        "NextAction": "Use only after response rows and family-level sign rule are exported.",
    },
    {
        "CandidateFamilyID": "RFAM_BACKREACTION_ENVELOPE_CONTROL",
        "FamilyType": "backreaction_control",
        "SourceProducts": "external_backreaction_envelope",
        "UsesPublicSN": False,
        "UsesPublicBAO": False,
        "CoordinateNativeTarget": False,
        "ResponseExportPath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "CurrentArtifact": "none",
        "CurrentStatus": "MISSING_CONTROL_SOURCE",
        "RequiredTransform": "external backreaction envelope mapped to source-split target rows",
        "RequiredCovariance": "declared covariance or envelope-to-sigma policy",
        "AllowedRole": "fair_null_later",
        "AllowedForK2ScoringNow": False,
        "BlockingIssue": "control_source_missing;coordinate_native_false",
        "NextAction": "Register only after public envelope source and mapping are declared.",
    },
    {
        "CandidateFamilyID": "RFAM_DYER_ROEDER_OPTICAL_CONTROL",
        "FamilyType": "optical_control",
        "SourceProducts": "external_dyer_roeder_or_optical_depth_control",
        "UsesPublicSN": False,
        "UsesPublicBAO": False,
        "CoordinateNativeTarget": False,
        "ResponseExportPath": "data/reconstruction_families/source_split_reconstruction_family_responses.csv",
        "CurrentArtifact": "none",
        "CurrentStatus": "MISSING_CONTROL_SOURCE",
        "RequiredTransform": "optical propagation response mapped to source-split target rows",
        "RequiredCovariance": "declared covariance or envelope-to-sigma policy",
        "AllowedRole": "fair_null_later",
        "AllowedForK2ScoringNow": False,
        "BlockingIssue": "control_source_missing;coordinate_native_false",
        "NextAction": "Register only after public optical-control source and mapping are declared.",
    },
]


def main() -> None:
    output = pd.DataFrame(CANDIDATES)
    output.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "PlanID": "SOURCE_SPLIT_RECONSTRUCTION_FAMILY_CANDIDATE_PLAN_V1",
                "CandidateFamilies": len(output),
                "CandidateInputsWithPublicSN": int(output["UsesPublicSN"].sum()),
                "CandidateInputsWithPublicBAO": int(output["UsesPublicBAO"].sum()),
                "CoordinateNativeCandidates": int(output["CoordinateNativeTarget"].sum()),
                "AllowedForK2ScoringNow": int(output["AllowedForK2ScoringNow"].sum()),
                "PrimaryNextAction": "Export SN and BAO residual branches into the reconstruction-family response schema.",
                "ClaimBoundary": "candidate_plan_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
