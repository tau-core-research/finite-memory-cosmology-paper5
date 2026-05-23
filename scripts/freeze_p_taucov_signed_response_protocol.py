#!/usr/bin/env python3
"""Freeze signed-response protocol for branch-localized P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
LOCAL_MAP = ROOT / "evidence/p_taucov_branch_localized_map_summary.csv"
STATISTIC = ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv"
OUT = ROOT / "evidence/p_taucov_signed_response_protocol.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_protocol_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_protocol.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_FREEZE_v1"
CLAIM_BOUNDARY = "signed_response_protocol_freeze_no_scoring"


def main() -> int:
    local = pd.read_csv(LOCAL_MAP).iloc[0]
    signed_required = bool(local["PositiveSemidefinite"]) is False
    statistic_frozen = False
    if STATISTIC.exists():
        statistic = pd.read_csv(STATISTIC).iloc[0]
        statistic_frozen = str(statistic["Status"]) == "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING"
    rows = [
        ("SR-01_SIGNED_MAP_REQUIRED", "localized map is signed/non-PSD, so covariance-survival scoring is forbidden", signed_required),
        ("SR-02_STATISTIC", "predeclare contrast S=trace((rr^T/sigma^2-I)K_signed) on held-out folds", statistic_frozen),
        ("SR-03_NULLS", "signed random, sign-flip, support-shuffle, morphology-null, and projection-null controls required", False),
        ("SR-04_AGGREGATION", "family and clock blocked rank/sign aggregation required", False),
        ("SR-05_NO_SURVIVAL_RESCUE", "signed diagnostic cannot rescue failed PSD primary score", True),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RuleID": rule_id,
                "Definition": definition,
                "Satisfied": bool(satisfied),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for rule_id, definition, satisfied in rows
        ]
    )
    table.to_csv(OUT, index=False)
    status = "P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_DECLARED_BLOCKED_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "SatisfiedRules": int(table["Satisfied"].sum()),
                "TotalRules": len(table),
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
                "# P-TauCov Signed-Response Protocol",
                "",
                f"Status: `{status}`.",
                "",
                "The branch-localized map is signed rather than PSD. Therefore it",
                "must not be scored as a covariance-deformation survival candidate.",
                "The allowed next path is a separate signed operator-contrast protocol.",
                "",
                "The eventual statistic must be frozen before scoring, for example:",
                "",
                "```math",
                "S = \\operatorname{tr}\\left[(rr^{\\mathsf T}/\\sigma^2-I)K_{\\rm signed}\\right].",
                "```",
                "",
                "This is an alignment statistic, not a covariance likelihood claim.",
                "It requires its own signed nulls and blocked aggregation.",
                "",
                "No scoring is authorized by this protocol declaration.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
