#!/usr/bin/env python3
"""Freeze signed-response blocked aggregation policy for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_signed_response_aggregation_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_aggregation_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_aggregation_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "signed_response_aggregation_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("AGG-01_PRIMARY_FAMILY", "primary", "leave-one-family-out signed statistic aggregate must be positive", "sum_S_family"),
        ("AGG-02_PRIMARY_CLOCK", "primary", "contiguous clock-block signed statistic aggregate must be positive", "sum_S_clock"),
        ("AGG-03_RANK_TEST", "primary", "primary signed statistic must rank above required signed nulls", "rank_against_required_nulls"),
        ("AGG-04_DOMINANCE_CAP", "primary", "largest positive family contribution share must be <= 0.5", "max_family_share_le_0p5"),
        ("AGG-05_SIGN_CONSISTENCY", "primary", "family and clock aggregate signs must agree", "same_sign_family_clock"),
        ("AGG-06_DIAGNOSTIC_REPORTING", "diagnostic", "family_x_clock and diagonal controls are report-only", "not_claim_rescue"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "AggregationID": agg_id,
                "AggregationClass": agg_class,
                "Definition": definition,
                "FrozenRule": rule,
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for agg_id, agg_class, definition, rule in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING",
                "AggregationRules": len(table),
                "PrimaryRules": int(table["AggregationClass"].eq("primary").sum()),
                "DominanceCap": 0.5,
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
                "# P-TauCov Signed-Response Aggregation Policy",
                "",
                "Status: `P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING`.",
                "",
                "A future signed-response score must pass both family and clock",
                "blocked aggregation. It must rank above required signed nulls, must",
                "not be dominated by one family, and family/clock signs must agree.",
                "",
                "The dominance cap is frozen at `0.5` for the largest positive family",
                "contribution share.",
                "",
                "Diagnostic family-by-clock and diagonal controls are report-only and",
                "cannot rescue a failed primary signed result.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_SIGNED_RESPONSE_AGGREGATION_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
