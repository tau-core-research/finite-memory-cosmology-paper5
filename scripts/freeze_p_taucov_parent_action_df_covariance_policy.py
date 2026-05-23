#!/usr/bin/env python3
"""Freeze parent-action P-TauCov df/covariance policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_parent_action_df_covariance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_df_covariance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_df_covariance_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "parent_action_df_covariance_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PARAM_ALPHA", "degrees_of_freedom", "single scalar alpha for C=C0+alpha*K_tau", "1"),
        ("ALPHA_DOMAIN", "parameter_bounds", "alpha is fitted under fixed PSD-preserving covariance constraints", "fixed_by_scorecard_regularizer"),
        ("KERNEL_POLICY", "kernel", "primary kernel is target-blind PSD covariance map from parent-action response", "PSD"),
        ("COVARIANCE_REGULARIZATION", "regularization", "use predeclared ridge/jitter only if required for numerical positive definiteness", "scorecard_declared"),
        ("INFORMATION_CRITERION", "model_comparison", "AIC and BIC count df=1 for the parent-action deformation", "df_1"),
        ("NO_SECONDARY_RESCUE", "claim_boundary", "diagnostic contrasts cannot rescue failed primary covariance score", "forbidden"),
    ]
    policy = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "PolicyID": policy_id,
                "PolicyClass": policy_class,
                "Definition": definition,
                "FrozenValue": value,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for policy_id, policy_class, definition, value in rows
        ]
    )
    policy.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING",
                "PolicyRows": len(policy),
                "DeclaredDF": 1,
                "PrimaryKernelPolicy": "PSD",
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Action DF/Covariance Policy",
                "",
                "Status: `P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING`.",
                "",
                "The future primary scorecard, if authorized, is a one-parameter",
                "covariance-deformation test:",
                "",
                "```math",
                "C = C_0 + \\alpha K_{\\tau}.",
                "```",
                "",
                "Information-criterion accounting uses `df=1`. The primary kernel is",
                "the target-blind PSD covariance map declared from the parent-action",
                "response. Diagnostic contrasts cannot rescue a failed primary result.",
                "",
                "This policy does not authorize scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PARENT_ACTION_DF_COVARIANCE_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
