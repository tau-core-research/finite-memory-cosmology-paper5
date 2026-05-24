#!/usr/bin/env python3
"""Freeze compact spectral fold policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_compact_spectral_fold_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_compact_spectral_fold_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_compact_spectral_fold_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COMPACT_SPECTRAL_FOLD_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "compact_spectral_fold_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PRIMARY_LOFO_FAMILY", "primary_leave_one_family_out", True, "reuse_preexisting_family_blocks_without_score_pattern"),
        ("PRIMARY_CLOCK_BLOCK", "primary_contiguous_clock_block", True, "required because source is compact-clock spectral"),
        ("PRIMARY_CONTEXT_BLOCK", "primary_observing_context_block", True, "required after expanded route context/dominance failures"),
        ("SECONDARY_INTERLEAVED_CLOCK", "secondary_interleaved_clock_holdout", False, "diagnostic_only_not_survival"),
        ("SECONDARY_FAMILY_X_CLOCK", "secondary_family_x_clock_block", False, "diagnostic_only_not_survival"),
    ]
    table = pd.DataFrame(
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
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_COMPACT_SPECTRAL_FOLD_POLICY_FROZEN_NO_SCORING",
                "FoldPolicies": len(table),
                "PrimaryFoldPolicies": int(table["Primary"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        """# P-TauCov Compact Spectral Fold Policy

Status: `P_TAUCOV_COMPACT_SPECTRAL_FOLD_POLICY_FROZEN_NO_SCORING`.

Compact spectral scoring, if later authorized, must aggregate over family,
clock, and observing-context primary folds. Interleaved clock and
family-by-clock folds are diagnostic only.
""",
        encoding="utf-8",
    )
    print("P_TAUCOV_COMPACT_SPECTRAL_FOLD_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
