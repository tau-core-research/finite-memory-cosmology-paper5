#!/usr/bin/env python3
"""Freeze PB zero-diagonal fold policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_pb_zero_diagonal_fold_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_pb_zero_diagonal_fold_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_pb_zero_diagonal_fold_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_FOLD_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "pb_zero_diagonal_fold_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("PRIMARY_LOFO_FAMILY", "primary_leave_one_family_out", True, "required after family-localization failures"),
        ("PRIMARY_CLOCK_BLOCK", "primary_contiguous_clock_block", True, "required because P*B is a branch/clock response object"),
        ("PRIMARY_CONTEXT_BLOCK", "primary_observing_context_block", True, "required after context/dominance failures"),
        ("SECONDARY_INTERLEAVED_CLOCK", "secondary_interleaved_clock_holdout", False, "diagnostic_only_not_survival"),
        ("SECONDARY_FAMILY_X_CLOCK", "secondary_family_x_clock_block", False, "diagnostic_only_not_survival"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "FoldPolicyID": pid,
                "FoldClass": cls,
                "Primary": bool(primary),
                "Source": source,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for pid, cls, primary, source in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_FOLD_POLICY_FROZEN_NO_SCORING",
                "FoldPolicies": len(table),
                "PrimaryFoldPolicies": int(table["Primary"].sum()),
                "PTauCovScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "# P-TauCov PB Zero-Diagonal Fold Policy\n\n"
        "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_FOLD_POLICY_FROZEN_NO_SCORING`.\n\n"
        "If later authorized, scoring must aggregate over family, contiguous clock,\n"
        "and observing-context primary folds. Secondary folds remain diagnostic only.\n",
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_FOLD_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
