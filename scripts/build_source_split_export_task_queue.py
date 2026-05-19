#!/usr/bin/env python3
"""Build the next export task queue for the source-split branch."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "source_split_export_task_queue.csv"
SUMMARY = EVIDENCE / "source_split_export_task_queue_summary.csv"


TASKS = [
    {
        "TaskID": "TQ1_COORDINATE_NATIVE_TRANSFORM",
        "DependsOn": "public_inputs;standardized_preflight",
        "UnlocksGate": "SS_TRANSFORM",
        "OutputTarget": "coordinate-native source-split diagnostic vector",
        "RequiredArtifact": "evidence/source_split_coordinate_native_target.csv",
        "DoneCriteria": "public SN and BAO rows mapped to one declared x coordinate with no K2 scoring",
        "Risk": "mixing SN and BAO residual units without a declared response scale",
        "Status": "COMPLETED_PREFLIGHT",
        "NextAction": "Use target as input for K1 and sign-family export; do not score K2 yet.",
    },
    {
        "TaskID": "TQ2_COORDINATE_NATIVE_K1",
        "DependsOn": "TQ1_COORDINATE_NATIVE_TRANSFORM",
        "UnlocksGate": "SS_K1_TARGET",
        "OutputTarget": "SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET",
        "RequiredArtifact": "evidence/source_split_k1_coordinate_native_target.csv",
        "DoneCriteria": "no-memory baseline fixed before K2 and not fit by K2 residuals",
        "Risk": "baseline absorbs finite-memory signal or uses same-data amplitude fit",
        "Status": "COMPLETED_CONTROL_PREFLIGHT",
        "NextAction": "Use as K1 control only after joint covariance and sign-family exist; do not score K2 yet.",
    },
    {
        "TaskID": "TQ3_JOINT_COVARIANCE",
        "DependsOn": "TQ1_COORDINATE_NATIVE_TRANSFORM;TQ2_COORDINATE_NATIVE_K1",
        "UnlocksGate": "SS_JOINT_COVARIANCE",
        "OutputTarget": "SSCOV_SHRINKAGE_SOURCE_SPLIT or SSCOV_PUBLIC_JOINT_SOURCE_SPLIT",
        "RequiredArtifact": "evidence/source_split_joint_covariance_policy.csv",
        "DoneCriteria": "declared covariance or shrinkage rule applies to the same target vector as K1",
        "Risk": "using diagonal/proxy covariance as if it were a public joint covariance",
        "Status": "COMPLETED_POLICY_PREFLIGHT",
        "NextAction": "Use as covariance policy only after public sign-family exists; do not score K2 yet.",
    },
    {
        "TaskID": "TQ4_PUBLIC_SIGN_FAMILY",
        "DependsOn": "TQ1_COORDINATE_NATIVE_TRANSFORM",
        "UnlocksGate": "SS_SIGN_FAMILY",
        "OutputTarget": "SF_PUBLIC_SOURCE_SPLIT_FAMILIES",
        "RequiredArtifact": "evidence/source_split_public_sign_family.csv",
        "DoneCriteria": "public reconstruction families and sign-stable rule exported on the same target rows",
        "Risk": "reusing distilled packet signs as if they were public source-split signs",
        "Status": "COMPLETED_BRANCH_SIGN_PREFLIGHT",
        "NextAction": "Replace branch-sign preflight with public reconstruction-family export before K2 scoring.",
    },
    {
        "TaskID": "TQ4_RECONSTRUCTION_FAMILY_UPGRADE",
        "DependsOn": "TQ4_PUBLIC_SIGN_FAMILY",
        "UnlocksGate": "SS_SIGN_FAMILY",
        "OutputTarget": "scoring-grade public reconstruction-family signs",
        "RequiredArtifact": "evidence/source_split_reconstruction_family_upgrade_contract.csv",
        "DoneCriteria": "public reconstruction-family signs are row-aligned and sign-stability rule is declared",
        "Risk": "treating branch-sign preflight as reconstruction-family evidence",
        "Status": "CONTRACT_EXPORTED_STILL_BLOCKED",
        "NextAction": "Export actual public reconstruction-family responses; do not score K2 from branch signs.",
    },
    {
        "TaskID": "TQ4A_CANDIDATE_EXPORT_SCHEMA",
        "DependsOn": "TQ4_RECONSTRUCTION_FAMILY_UPGRADE",
        "UnlocksGate": "SS_RECONSTRUCTION_FAMILY_EXPORT",
        "OutputTarget": "public reconstruction-family response schema",
        "RequiredArtifact": "evidence/source_split_reconstruction_family_export_schema.csv",
        "DoneCriteria": "long-format schema and empty template exist for the candidate export",
        "Risk": "schema drift between preview artifacts and scoring candidate path",
        "Status": "COMPLETED_SCHEMA_PREFLIGHT",
        "NextAction": "Use schema for candidate export; do not score K2 from the empty template.",
    },
    {
        "TaskID": "TQ4B_CANDIDATE_EXPORT_PREVIEW",
        "DependsOn": "TQ4A_CANDIDATE_EXPORT_SCHEMA",
        "UnlocksGate": "SS_RECONSTRUCTION_FAMILY_PREVIEW",
        "OutputTarget": "non-scoring reconstruction-family response preview",
        "RequiredArtifact": "evidence/source_split_reconstruction_family_response_preview.csv",
        "DoneCriteria": "SN and BAO branch residuals can be represented in the frozen schema",
        "Risk": "mistaking schema-valid preview rows for scoring candidate rows",
        "Status": "COMPLETED_PREVIEW_NOT_SCORING",
        "NextAction": "Create a real candidate export under data/reconstruction_families before scoring.",
    },
    {
        "TaskID": "TQ4C_SIGN_RULE_PROMOTION",
        "DependsOn": "TQ4B_CANDIDATE_EXPORT_PREVIEW",
        "UnlocksGate": "SS_SIGN_RULE_PROMOTION",
        "OutputTarget": "scoring-grade family sign-stability rule",
        "RequiredArtifact": "evidence/source_split_sign_rule_promotion_readiness.csv",
        "DoneCriteria": "valid candidate export exists and warning rows are retained under a locked scoring rule",
        "Risk": "using preview sign warnings as scoring evidence before candidate export exists",
        "Status": "BLOCKED_BY_CANDIDATE_EXPORT",
        "NextAction": "Promote only after data/reconstruction_families/source_split_reconstruction_family_responses.csv validates cleanly.",
    },
    {
        "TaskID": "TQ5_LOCKED_K2_SCORECARD",
        "DependsOn": "TQ2_COORDINATE_NATIVE_K1;TQ3_JOINT_COVARIANCE;TQ4C_SIGN_RULE_PROMOTION",
        "UnlocksGate": "SS_K2_SCORING",
        "OutputTarget": "source-split K2/null scorecard",
        "RequiredArtifact": "evidence/source_split_k2_scoring_authorization.csv",
        "DoneCriteria": "authorization guard returns AUTHORIZED before locked p=3 rho<=4 K2 and nulls are scored",
        "Risk": "premature K2 scoring before baseline/covariance/sign-family are frozen",
        "Status": "BLOCKED_BY_AUTHORIZATION_GUARD",
        "NextAction": "Do not run until source_split_k2_scoring_authorization.csv returns AUTHORIZED.",
    },
]


def main() -> None:
    tasks = pd.DataFrame(TASKS)
    tasks.to_csv(OUT, index=False)

    summary = pd.DataFrame(
        [
            {
                "QueueID": "SOURCE_SPLIT_EXPORT_TASK_QUEUE",
                "Tasks": len(tasks),
                "NextTask": "TQ4C_SIGN_RULE_PROMOTION",
                "BlockedTasks": int(tasks["Status"].astype(str).str.contains("BLOCKED").sum()),
                "K2ScoringTask": "TQ5_LOCKED_K2_SCORECARD",
                "K2ScoringStatus": "blocked",
                "ClaimBoundary": "task_queue_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
