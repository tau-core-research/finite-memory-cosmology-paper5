#!/usr/bin/env python3
"""Freeze the parent-action P-TauCov fold policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_parent_action_fold_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_fold_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_fold_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "parent_action_fold_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PRIMARY_LOFO_FAMILY", "primary_leave_one_family_out", True, "reuse_preexisting_family_blocks_without_score_pattern"),
        ("PRIMARY_CLOCK_BLOCK", "primary_contiguous_clock_block", True, "reuse_preexisting_clock_blocks_without_score_pattern"),
        ("SECONDARY_FAMILY_X_CLOCK", "secondary_family_x_clock_block", False, "diagnostic_only_not_survival"),
        ("STRESS_OUTSIDE_BRANCH", "outside_declared_branch_support", False, "negative_control_diagnostic_only"),
    ]
    policy = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FoldPolicyID": policy_id,
                "FoldClass": fold_class,
                "Primary": bool(primary),
                "Source": source,
                "RandomRowShufflePrimaryForbidden": True,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for policy_id, fold_class, primary, source in rows
        ]
    )
    policy.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FROZEN_NO_SCORING",
                "FoldPolicies": len(policy),
                "PrimaryFoldPolicies": int(policy["Primary"].sum()),
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
                "# P-TauCov Parent-Action Fold Policy",
                "",
                "Status: `P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FROZEN_NO_SCORING`.",
                "",
                "Primary scoring, if later authorized, must aggregate over both",
                "leave-one-family-out and contiguous clock-block folds. Secondary",
                "family-by-clock and outside-branch folds are diagnostic only.",
                "",
                "No target residuals, score outcomes, alpha behavior, or family-win",
                "patterns are allowed to define this policy.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PARENT_ACTION_FOLD_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
