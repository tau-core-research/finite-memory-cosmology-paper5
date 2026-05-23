#!/usr/bin/env python3
"""Freeze family-balance policy for the next P-TauCov candidate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FOLDS = ROOT / "evidence/backreaction_36_fold_design.csv"
TARGET = ROOT / "data/physical_nulls/backreaction_reproduction/registered_protocol_guided_reproduction_backreaction_vector.csv"
OUT = ROOT / "evidence/p_taucov_family_balance_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_family_balance_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_family_balance_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_FAMILY_BALANCE_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "family_balance_policy_freeze_no_scoring"


def main() -> int:
    rows = pd.read_csv(TARGET)
    family_counts = rows.groupby("FamilyID").size().reset_index(name="Rows")
    total_rows = int(family_counts["Rows"].sum())
    family_counts["RowShare"] = family_counts["Rows"] / total_rows
    family_counts["MaxAllowedPositiveContributionShare"] = 0.5
    family_counts["MinPositiveFamiliesRequired"] = 2
    family_counts["TargetResidualsUsedForPolicy"] = False
    family_counts["ScoreOutcomeUsedForPolicy"] = False
    family_counts["ScoringAuthorized"] = False
    family_counts["ProtocolID"] = PROTOCOL_ID
    family_counts["FreezeID"] = FREEZE_ID
    family_counts["ClaimBoundary"] = CLAIM_BOUNDARY
    family_counts[
        [
            "ProtocolID",
            "FreezeID",
            "FamilyID",
            "Rows",
            "RowShare",
            "MaxAllowedPositiveContributionShare",
            "MinPositiveFamiliesRequired",
            "TargetResidualsUsedForPolicy",
            "ScoreOutcomeUsedForPolicy",
            "ScoringAuthorized",
            "ClaimBoundary",
        ]
    ].to_csv(OUT, index=False)
    folds = pd.read_csv(FOLDS)
    lofo_count = int(folds["FoldClass"].eq("primary_leave_one_family_out").sum())
    clock_count = int(folds["FoldClass"].eq("primary_contiguous_clock_block").sum())
    status = "P_TAUCOV_FAMILY_BALANCE_POLICY_FROZEN_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "Families": len(family_counts),
                "TotalRows": total_rows,
                "PrimaryLOFOFolds": lofo_count,
                "PrimaryClockFolds": clock_count,
                "MaxAllowedPositiveContributionShare": 0.5,
                "MinPositiveFamiliesRequired": 2,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Family-Balance Policy",
                "",
                f"Status: `{status}`.",
                "",
                "A future candidate cannot pass if its positive signed/alignment",
                "contribution is effectively carried by one family.",
                "",
                "Frozen requirements:",
                "",
                "- at least `2` positive contributing families;",
                "- largest positive family contribution share must be `<= 0.5`;",
                "- leave-one-family-out folds remain primary;",
                "- clock-block folds remain primary.",
                "",
                "This policy uses only family labels and row counts, not target",
                "residuals or score outcomes.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
