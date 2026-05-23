#!/usr/bin/env python3
"""Freeze covariance treatment policy for Backreaction-36."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT = EVIDENCE / "backreaction_36_covariance_treatment.csv"
SUMMARY = EVIDENCE / "backreaction_36_covariance_treatment_summary.csv"
DOC = DOCS / "backreaction_36_covariance_treatment.md"

PROTOCOL_ID = "P5B_BACKREACTION_36_FROZEN_MORPHOLOGY_PROTOCOL_v1"
CLAIM_BOUNDARY = "backreaction_36_covariance_policy_no_target_covariance_preselection"


POLICIES = [
    (
        "C0_PRIMARY",
        "primary",
        "diagonal_equal_weight_chi2",
        "Equal/diagonal weights; no full-target covariance fit.",
        True,
    ),
    (
        "C1_ROBUSTNESS",
        "robustness",
        "family_block_aggregate_weighting",
        "Family-block aggregate weighting or family-cluster robust score.",
        True,
    ),
    (
        "C2_ROBUSTNESS",
        "robustness",
        "shrinkage_covariance_if_target_blind_or_training_fold_only",
        "Shrinkage covariance only if target-blind or estimated within training folds.",
        True,
    ),
    (
        "FORBIDDEN_FULL_TARGET_COVARIANCE",
        "forbidden",
        "full_target_covariance_fit_before_scoring",
        "Full-target covariance fitted before scoring is forbidden.",
        False,
    ),
    (
        "FORBIDDEN_SCORE_CHOSEN_COVARIANCE",
        "forbidden",
        "covariance_chosen_based_on_score",
        "Covariance treatment may not be selected based on benchmark performance.",
        False,
    ),
]


def main() -> int:
    rows = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "CovarianceID": cid,
                "Role": role,
                "Treatment": treatment,
                "Definition": definition,
                "AllowedForScoring": allowed,
                "FrozenBeforeCandidate": True,
                "UsesFullTargetCovariancePreScoring": False,
                "CanBeChosenByScore": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for cid, role, treatment, definition, allowed in POLICIES
        ]
    )
    rows.to_csv(OUT, index=False)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "CovariancePolicies": len(rows),
                "PrimaryCovariance": "C0_PRIMARY",
                "RobustnessCovariances": "C1_ROBUSTNESS;C2_ROBUSTNESS",
                "FullTargetCovariancePreScoringForbidden": True,
                "ScoreChosenCovarianceForbidden": True,
                "CurrentStatus": "COVARIANCE_TREATMENT_FROZEN",
                "ScoringAuthorizedByThisArtifact": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# Backreaction-36 Covariance Treatment",
                "",
                "Status: covariance policy frozen; scoring is not authorized by this artifact.",
                "",
                "- Primary: `C0_PRIMARY` diagonal/equal-weight chi2.",
                "- Robustness: `C1_ROBUSTNESS` family-block aggregate weighting.",
                "- Robustness: `C2_ROBUSTNESS` shrinkage covariance if target-blind or training-fold-only.",
                "",
                "Forbidden:",
                "",
                "- full-target covariance fitted before scoring;",
                "- covariance choice based on score.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for path in [OUT, SUMMARY, DOC]:
        print(f"wrote {path.relative_to(ROOT)}")
    print("COVARIANCE_TREATMENT_FROZEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
