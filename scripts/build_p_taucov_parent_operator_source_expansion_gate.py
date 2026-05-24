#!/usr/bin/env python3
"""Freeze the parent-operator source expansion gate for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

CEILING = EVIDENCE / "p_taucov_active_triad_psd_ceiling_audit_summary.csv"
SOURCE_CANDIDATES = EVIDENCE / "p_taucov_coordinate_basis_source_candidates.csv"
DOMAIN = EVIDENCE / "p_taucov_full_action_domain_coordinates.csv"

OUT = EVIDENCE / "p_taucov_parent_operator_source_expansion_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_parent_operator_source_expansion_gate_summary.csv"
DOC = DOCS / "p_taucov_parent_operator_source_expansion_gate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_v1"
CLAIM_BOUNDARY = "parent_operator_source_expansion_gate_no_scoring"


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    ceiling = pd.read_csv(CEILING).iloc[0]
    sources = pd.read_csv(SOURCE_CANDIDATES)
    domain = pd.read_csv(DOMAIN)

    active_count = int(domain["InReducedDomain"].astype(bool).sum())
    allowed_sources = set(
        sources.loc[sources["AllowedForCandidateBasis"].astype(bool), "CandidateSource"].astype(str)
    )
    forbidden_sources = set(
        sources.loc[~sources["AllowedForCandidateBasis"].astype(bool), "CandidateSource"].astype(str)
    )
    ceiling_blocks = str(ceiling["Status"]) == "P_TAUCOV_ACTIVE_TRIAD_PSD_CEILING_BLOCKS_SCORING_NO_SCORING"

    required_allowed = {
        "TauSideSymbolicDefinition",
        "CoordinateConventionOnly",
        "PublishedExternalMetadata",
    }
    required_forbidden = {
        "ExistingP5CKernelV3Gains",
        "HeldOutResidualsOrTargets",
        "PostHocFamilyLocalization",
        "GenericSmoothNullTemplates",
    }

    rows = [
        (
            "POSE-G1_ACTIVE_TRIAD_CEILING_CONFIRMED",
            ceiling_blocks,
            "the current Phi/B/P PSD route is structurally too narrow",
        ),
        (
            "POSE-G2_ALLOWED_SOURCE_CLASSES_AVAILABLE",
            required_allowed.issubset(allowed_sources),
            "allowed source classes exist for non-outcome expansion",
        ),
        (
            "POSE-G3_FORBIDDEN_SOURCE_CLASSES_DECLARED",
            required_forbidden.issubset(forbidden_sources),
            "outcome-leaking source classes are explicitly forbidden",
        ),
        (
            "POSE-G4_EXPANDED_DOMAIN_REQUIRED",
            True,
            "next PSD candidate must use more active support than the three-coordinate triad",
        ),
        (
            "POSE-G5_MINIMUM_ACTIVE_COORDINATES_GE_5",
            True,
            "expanded parent-operator packet must declare at least five active reduced coordinates",
        ),
        (
            "POSE-G6_AT_LEAST_TWO_NEW_NONOUTCOME_AXES",
            True,
            "at least two added axes must come from allowed source classes and not from score outcomes",
        ),
        (
            "POSE-G7_OPERATOR_SOURCE_BEFORE_MATRIX",
            True,
            "new axes must be justified by a parent-side operator/source rule before covariance lifting",
        ),
        (
            "POSE-G8_NO_RECLASSIFYING_FORBIDDEN_AXES_WITHOUT_NEW_PACKET",
            True,
            "forbidden or gauge axes may not be reused unless a new domain packet changes their role target-blindly",
        ),
        (
            "POSE-G9_NO_SCORE_OR_TARGET_ACCESS",
            True,
            "this gate uses only no-score structural artifacts",
        ),
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "Requirement": requirement,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, requirement in rows
        ]
    )
    table.to_csv(OUT, index=False)
    status = (
        "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_READY_NO_OBJECT_NO_SCORING"
        if bool(table["Passed"].all())
        else "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CurrentActiveReducedCoordinateCount": active_count,
                "RequiredNextActiveReducedCoordinateCount": 5,
                "RequiredNewNonOutcomeAxes": 2,
                "AllowedSourceClasses": ";".join(sorted(allowed_sources)),
                "ForbiddenSourceClasses": ";".join(sorted(forbidden_sources)),
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Parent-Operator Source Expansion Gate

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The active-triad PSD ceiling audit shows that the current reduced coordinate
triad is structurally too narrow for the PSD covariance route. This gate
freezes what a broader parent-side operator/source packet must provide before
any new covariance object can be assembled.

## Why Expansion Is Required

The current active reduced domain has `{active_count}` active coordinates. The
existing `Phi/B/P` triad cannot pass the diagonal-energy and effective-rank
specificity gates under target-blind PSD lifting.

Therefore the next PSD route must not tune `Phi/B/P` weights. It must expand
the parent-side source space using allowed, non-outcome source classes.

## Allowed Source Classes

The only allowed expansion sources are:

- `TauSideSymbolicDefinition`
- `CoordinateConventionOnly`
- `PublishedExternalMetadata`

Forbidden sources remain:

- `ExistingP5CKernelV3Gains`
- `HeldOutResidualsOrTargets`
- `PostHocFamilyLocalization`
- `GenericSmoothNullTemplates`

## Next-Packet Requirements

A future expanded parent-operator packet must:

1. declare at least `5` active reduced coordinates;
2. add at least `2` non-outcome axes beyond the current `Phi/B/P` triad;
3. justify each new axis by an allowed source class;
4. define a parent-side operator/source rule before covariance lifting;
5. include a leakage audit against target residuals, score outcomes, P5C gains,
   and post-hoc family localization;
6. keep scoring blocked until an object-specific preflight passes.

## Claim Boundary

Allowed statement:

> The next PSD covariance route requires a broader target-blind parent-operator
> source space than the current active triad.

Forbidden statement:

> This gate constructs an expanded object, authorizes scoring, or validates Tau
> Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
