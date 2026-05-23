#!/usr/bin/env python3
"""Freeze parent-action P-TauCov null comparator policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_parent_action_null_comparators.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_null_comparators_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_null_comparators.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FREEZE_v1"
CLAIM_BOUNDARY = "parent_action_null_comparators_freeze_no_scoring"


def main() -> int:
    rows = [
        ("OUTSIDE_BRANCH", "localization_control", "score complement of declared branch support", True, True),
        ("SHUFFLED_SUPPORT", "support_null", "shuffle branch support preserving selected-cell count", True, True),
        ("MORPHOLOGY_NULL", "morphology_null", "preserve morphology energy while destroying branch-relaxation structure", True, True),
        ("PROJECTION_NULL", "projection_null", "preserve support while breaking parent projection coupling", True, True),
        ("GENERIC_RANDOM_SMOOTH_PSD", "generic_baseline", "strongest declared random smooth PSD comparator", True, True),
        ("GENERIC_FAMILY_PERMUTED", "generic_baseline", "family-permuted branch structure", True, True),
        ("GENERIC_DIAGONAL", "generic_baseline", "diagonal variance inflation comparator", True, True),
        ("GENERIC_WRONG_CLOCK", "generic_baseline", "wrong-clock support comparator", True, True),
        ("GENERIC_PHASE_SHIFT", "generic_baseline", "phase-shift support comparator", True, True),
        ("OSCILLATORY_DIAGNOSTIC", "diagnostic_control", "oscillatory geometry diagnostic; not eligible for survival defeat", False, False),
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
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FROZEN_NO_SCORING",
                "NullComparators": len(policy),
                "RequiredNullComparators": int(policy["Required"].sum()),
                "PrimaryDefeatRequired": int(policy["PrimaryDefeatRequired"].sum()),
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
                "# P-TauCov Parent-Action Null Comparators",
                "",
                "Status: `P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FROZEN_NO_SCORING`.",
                "",
                "A later parent-action scorecard must defeat all required primary",
                "comparators before any survival language is allowed. The diagnostic",
                "oscillatory comparator may be reported, but it cannot rescue or kill",
                "the primary claim by itself.",
                "",
                "Required classes:",
                "",
                "- outside-branch localization control",
                "- shuffled support null",
                "- morphology null",
                "- projection null",
                "- generic random smooth PSD",
                "- family-permuted, diagonal, wrong-clock, and phase-shift baselines",
                "",
                "No target residuals, score outcomes, alpha behavior, or family-win",
                "patterns are used to define this null policy.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PARENT_ACTION_NULL_COMPARATORS_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
