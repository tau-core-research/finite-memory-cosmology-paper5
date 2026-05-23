#!/usr/bin/env python3
"""Freeze complexity and degrees-of-freedom policy for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "backreaction_36_df_policy.csv"
SUMMARY = EVIDENCE / "backreaction_36_df_policy_summary.csv"
DOC = DOCS / "backreaction_36_df_policy.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_df_policy_single_primary_no_best_of_many"


MODELS = [
    ("POLY_DEG2", 3, "intercept + x + x^2", "baseline_absorber"),
    ("POLY_DEG2_PLUS_M_BSTAR_36", 4, "intercept + x + x^2 + one scalar M_BSTAR amplitude", "primary_candidate_model"),
    ("POLY_DEG2_PLUS_WRONG_CLOCK_BSTAR", 4, "same df as real M_BSTAR model", "negative_control"),
    ("POLY_DEG2_PLUS_PHASE_SHIFTED_BSTAR", 4, "same df as real M_BSTAR model", "negative_control"),
    ("POLY_DEG2_PLUS_FAMILY_PERMUTED_BSTAR", 4, "same df as real M_BSTAR model", "negative_control"),
    ("POLY_DEG2_PLUS_RANDOM_SMOOTH_NULL", 4, "same df as real M_BSTAR model", "negative_control"),
]


def main() -> int:
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "ModelID": model_id,
                "DF": df,
                "ParameterPolicy": params,
                "ModelClass": model_class,
                "ShapeDFAfterFreeze": 0 if "M_BSTAR" in model_id or "BSTAR" in model_id or "NULL" in model_id else "",
                "AmplitudeDF": 1 if model_id != "POLY_DEG2" else 0,
                "FrozenBeforeScoring": True,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for model_id, df, params, model_class in MODELS
        ]
    )
    rows.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "Models": len(rows),
                "PrimaryCandidateLimit": 1,
                "OnlyOnePrimaryMStarCandidateMayBeScored": True,
                "BestOfManyForbiddenWithoutPredeclaredCorrection": True,
                "AICcAndBICRequired": True,
                "CurrentStatus": "COMPLEXITY_DF_POLICY_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Complexity / DF Policy",
                "",
                "Status: complexity policy frozen; scoring is not authorized by this artifact.",
                "",
                "- `POLY_DEG2`: df = 3.",
                "- `POLY_DEG2 + M_BSTAR_36`: df = 4.",
                "- Frozen M_BSTAR shape: df = 0 after freeze.",
                "- Null Bstar-like controls carry the same df as the real M_BSTAR model.",
                "- Only one primary M_BSTAR_36 candidate may be scored.",
                "- Best-of-many candidate selection is forbidden unless correction is predeclared.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("COMPLEXITY_DF_POLICY_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
