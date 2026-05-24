#!/usr/bin/env python3
"""Freeze the expanded parent-operator fold policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_fold_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_fold_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_fold_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FOLD_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_fold_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PRIMARY_LOFO_FAMILY", "primary_leave_one_family_out", True, "reuse_preexisting_family_blocks_without_score_pattern"),
        ("PRIMARY_CLOCK_BLOCK", "primary_contiguous_clock_block", True, "reuse_preexisting_clock_blocks_without_score_pattern"),
        ("PRIMARY_CONTEXT_BLOCK", "primary_observing_context_block", True, "required because expanded object includes observing-context axis"),
        ("SECONDARY_FAMILY_X_CONTEXT", "secondary_family_x_context_block", False, "diagnostic_only_not_survival"),
        ("STRESS_OUTSIDE_EXPANDED_SUPPORT", "outside_declared_expanded_support", False, "negative_control_diagnostic_only"),
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
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for policy_id, fold_class, primary, source in rows
        ]
    )
    policy.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_FOLD_POLICY_FROZEN_NO_SCORING",
                "FoldPolicies": len(policy),
                "PrimaryFoldPolicies": int(policy["Primary"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        """# P-TauCov Expanded Parent-Operator Fold Policy

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_FOLD_POLICY_FROZEN_NO_SCORING`.

The expanded object must aggregate over family, clock, and observing-context
primary folds. Family-by-context and outside-expanded-support folds are
diagnostic only.

No target residuals, score outcomes, alpha behavior, or family-win patterns are
allowed to define this policy.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_FOLD_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
