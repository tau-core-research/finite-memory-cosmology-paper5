#!/usr/bin/env python3
"""Freeze signed-response statistic definition for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_signed_response_statistic.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_statistic_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_statistic.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FREEZE_v1"
CLAIM_BOUNDARY = "signed_response_statistic_freeze_no_scoring"


def main() -> int:
    rows = [
        ("STATISTIC", "S = trace((r r^T / sigma2 - I) K_signed)", "primary_signed_alignment_statistic"),
        ("RESIDUAL_SOURCE", "held-out residuals from the already frozen polynomial baseline machinery", "no_new_mean_model"),
        ("SIGMA_POLICY", "sigma2 fitted on training residuals only", "train_only"),
        ("KERNEL_POLICY", "K_signed is the frozen branch-localized signed map", "frozen_before_scoring"),
        ("SIGN_CONVENTION", "positive S means residual outer-product aligns with K_signed", "fixed"),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RuleID": rule_id,
                "Definition": definition,
                "FrozenValue": value,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for rule_id, definition, value in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING",
                "Statistic": "trace((rrT/sigma2-I)K_signed)",
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
                "# P-TauCov Signed-Response Statistic",
                "",
                "Status: `P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING`.",
                "",
                "The signed-response statistic is frozen as:",
                "",
                "```math",
                "S = \\operatorname{tr}\\left[(rr^{\\mathsf T}/\\sigma^2-I)K_{\\rm signed}\\right].",
                "```",
                "",
                "A positive value means the held-out residual outer product aligns with",
                "the frozen signed branch-localized operator. This is not a covariance",
                "likelihood score and not a survival claim.",
                "",
                "No scoring is authorized by this statistic freeze.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
