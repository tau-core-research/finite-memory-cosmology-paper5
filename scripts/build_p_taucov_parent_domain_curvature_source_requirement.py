#!/usr/bin/env python3
"""Define the next P-TauCov parent-domain curvature source requirement."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_v1"
STATUS = "P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_DEFINED_NO_OBJECT_NO_SCORING"
CLAIM = "parent_domain_curvature_source_requirement_no_object_no_scoring"

OUT_REQ = EVIDENCE / "p_taucov_parent_domain_curvature_source_requirement.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_parent_domain_curvature_source_requirement_summary.csv"
OUT_DOC = DOCS / "p_taucov_parent_domain_curvature_source_requirement.md"


REQUIREMENTS = [
    (
        "PDCS-R1_PARENT_DOMAIN_ORIGIN",
        "The source must be derived from an explicit parent-domain curvature, Hessian, boundary, or self-adjoint-domain term.",
        "required",
    ),
    (
        "PDCS-R2_NOT_CLEANER_GENERATED",
        "The source may be tested with Q_clean, but it must not be defined as Q_clean K Q_clean without an independent parent origin.",
        "forbidden_shortcut",
    ),
    (
        "PDCS-R3_COMMON_CLEAN_SUPPORT",
        "Support retention norm(Q_clean K Q_clean) / norm(K) must pass the frozen common-clean threshold before scoring.",
        ">=0.20",
    ),
    (
        "PDCS-R4_LOW_PROJECTION_LEAKAGE",
        "Projection leakage after common-clean restriction must remain below the frozen threshold.",
        "<=0.10",
    ),
    (
        "PDCS-R5_BRANCH_BALANCED_SUPPORT",
        "No single family, clock, or observing-context block may dominate pre-score energy.",
        "<=0.50",
    ),
    (
        "PDCS-R6_DIAGONAL_CONTROL",
        "The object must not reduce to diagonal variance inflation.",
        "<=0.10",
    ),
    (
        "PDCS-R7_NULL_SEPARATION_REQUIRED",
        "The object must remain separated from morphology-null, projection-null, shuffled-support, and generic smooth baselines before scoring authorization.",
        "required",
    ),
    (
        "PDCS-R8_TARGET_BLINDNESS",
        "No target residuals, OOS scores, fitted alpha behavior, or winning null information may enter source construction.",
        "required",
    ),
]


def main() -> int:
    rows = [
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "RequirementID": req_id,
            "Definition": definition,
            "ThresholdOrPolicy": policy,
            "ObjectConstructed": False,
            "ScoringAuthorized": False,
            "SurvivalClaimAuthorized": False,
            "TauCoreValidationClaimAuthorized": False,
            "ClaimBoundary": CLAIM,
        }
        for req_id, definition, policy in REQUIREMENTS
    ]
    pd.DataFrame(rows).to_csv(OUT_REQ, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "Requirements": len(REQUIREMENTS),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Parent-Domain Curvature Source Requirement",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{STATUS}`",
                "",
                "## Why This Gate Exists",
                "",
                "The compact spectral scorecard failed as an empirical covariance",
                "survivor, and the TCCS/common-clean sequence showed a sharper",
                "structural blocker: existing parent-derived candidates do not place",
                "enough energy into the frozen projection-orthogonal, branch-balanced",
                "clean subspace.",
                "",
                "Therefore the next object is not another scorecard variant. It must be",
                "a parent-domain curvature source whose clean-subspace support is a",
                "pre-score property.",
                "",
                "## Requirement Table",
                "",
                "| Requirement | Policy | Meaning |",
                "|---|---:|---|",
                *[
                    f"| `{req_id}` | `{policy}` | {definition} |"
                    for req_id, definition, policy in REQUIREMENTS
                ],
                "",
                "## Forbidden Shortcut",
                "",
                "A future candidate must not be created by taking an arbitrary matrix and",
                "declaring its cleaned version to be the Tau object:",
                "",
                "```text",
                "K_tau := Q_clean K_arbitrary Q_clean",
                "```",
                "",
                "Cleaning may be used as an audit. It may not be the source of the",
                "physics. The source must come from a declared parent-domain term first.",
                "",
                "## Current Status",
                "",
                "This artifact defines the next gate only. It constructs no object and",
                "authorizes no empirical scoring.",
                "",
                "Relevant precursor audits:",
                "",
                "- [`p_taucov_compact_spectral_scorecard.md`](p_taucov_compact_spectral_scorecard.md)",
                "- [`p_taucov_tccs_transfer_curvature_preflight.md`](p_taucov_tccs_transfer_curvature_preflight.md)",
                "- [`p_taucov_common_clean_subspace_support_audit.md`](p_taucov_common_clean_subspace_support_audit.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> The next P-TauCov object class must be parent-domain sourced and pass common-clean support before scoring.",
                "",
                "Forbidden statement:",
                "",
                "> This requirement defines a Tau signal, constructs a covariance survivor, or validates Tau Core.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
