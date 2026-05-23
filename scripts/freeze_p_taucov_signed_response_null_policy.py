#!/usr/bin/env python3
"""Freeze signed-response null policy for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence/p_taucov_signed_response_null_policy.csv"
SUMMARY = ROOT / "evidence/p_taucov_signed_response_null_policy_summary.csv"
DOC = ROOT / "docs/p_taucov_signed_response_null_policy.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FREEZE_v1"
CLAIM_BOUNDARY = "signed_response_null_policy_freeze_no_scoring"


def main() -> int:
    rows = [
        ("SIGNED_RANDOM_ORTHOGONAL", "signed_operator_null", "random signed operator with matched Frobenius norm and zero target access", True),
        ("SIGN_FLIP", "signed_operator_null", "flip signs on frozen branch-localized support while preserving absolute support", True),
        ("SUPPORT_SHUFFLE", "support_null", "shuffle signed support positions preserving selected-cell count", True),
        ("MORPHOLOGY_NULL", "morphology_null", "preserve morphology-like mass while breaking signed branch orientation", True),
        ("PROJECTION_NULL", "projection_null", "preserve support but break parent projection/source orientation", True),
        ("FAMILY_PERMUTED", "blocked_null", "permute family labels before blocked aggregation", True),
        ("CLOCK_PHASE_SHIFT", "blocked_null", "phase-shift clock blocks before blocked aggregation", True),
        ("DIAGONAL_SIGNED_CONTROL", "diagnostic_control", "signed diagonal diagnostic only; cannot rescue or kill primary", False),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "NullID": null_id,
                "NullClass": null_class,
                "Definition": definition,
                "RequiredForSignedClaim": bool(required),
                "TargetResidualsUsedForPolicy": False,
                "ScoreOutcomeUsedForPolicy": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for null_id, null_class, definition, required in rows
        ]
    )
    table.to_csv(OUT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING",
                "Nulls": len(table),
                "RequiredNulls": int(table["RequiredForSignedClaim"].sum()),
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
                "# P-TauCov Signed-Response Null Policy",
                "",
                "Status: `P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING`.",
                "",
                "A signed-response alignment claim must beat required signed and",
                "blocked nulls: random signed, sign-flip, support-shuffle, morphology,",
                "projection, family-permuted, and clock phase-shift controls.",
                "",
                "The diagonal signed control is diagnostic only. It cannot rescue a",
                "failed signed primary result and cannot by itself kill an otherwise",
                "valid result.",
                "",
                "No target residuals or score outcomes are used to define this policy.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_SIGNED_RESPONSE_NULL_POLICY_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
