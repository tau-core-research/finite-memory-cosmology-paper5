#!/usr/bin/env python3
"""Freeze expanded parent-operator null comparator policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_null_comparators.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_null_comparators_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_null_comparators.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_NULL_COMPARATORS_FREEZE_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_null_comparators_freeze_no_scoring"


def main() -> int:
    rows = [
        ("OUTSIDE_EXPANDED_SUPPORT", "localization_control", "score complement of declared expanded support", True, True),
        ("SHUFFLED_EXPANDED_SUPPORT", "support_null", "shuffle expanded support preserving active-cell count", True, True),
        ("MORPHOLOGY_NULL", "morphology_null", "preserve morphology-like energy while destroying branch-relaxation structure", True, True),
        ("PROJECTION_NULL", "projection_null", "preserve support while breaking parent projection coupling", True, True),
        ("SCALE_ONLY_NULL", "expanded_axis_null", "retain coordinate-scale axis but remove Phi/B/P coupling", True, True),
        ("CONTEXT_ONLY_NULL", "expanded_axis_null", "retain observing-context axis but remove parent-source contrast", True, True),
        ("GENERIC_RANDOM_SMOOTH_PSD", "generic_baseline", "strongest declared random smooth PSD comparator", True, True),
        ("GENERIC_DIAGONAL", "generic_baseline", "diagonal variance inflation comparator", True, True),
        ("GENERIC_FAMILY_PERMUTED", "generic_baseline", "family-permuted structure", True, True),
        ("GENERIC_WRONG_CLOCK", "generic_baseline", "wrong-clock support comparator", True, True),
        ("GENERIC_PHASE_SHIFT", "generic_baseline", "phase-shift support comparator", True, True),
    ]
    policy = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "NullID": null_id,
                "NullClass": null_class,
                "Definition": definition,
                "Required": bool(required),
                "PrimaryDefeatRequired": bool(primary_defeat),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for null_id, null_class, definition, required, primary_defeat in rows
        ]
    )
    policy.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_EXPANDED_PARENT_OPERATOR_NULL_COMPARATORS_FROZEN_NO_SCORING",
                "NullComparators": len(policy),
                "RequiredNullComparators": int(policy["Required"].sum()),
                "PrimaryDefeatRequired": int(policy["PrimaryDefeatRequired"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        """# P-TauCov Expanded Parent-Operator Null Comparators

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_NULL_COMPARATORS_FROZEN_NO_SCORING`.

A later expanded scorecard must defeat all required primary comparators,
including scale-only and context-only nulls introduced specifically because the
expanded candidate uses those non-outcome axes.

No target residuals, score outcomes, alpha behavior, or family-win patterns are
used to define this null policy.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_NULL_COMPARATORS_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
