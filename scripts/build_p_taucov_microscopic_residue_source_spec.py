#!/usr/bin/env python3
"""Build the no-score microscopic residue source specification."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCE_GAP = EVIDENCE / "p_taucov_parent_source_gap_packet_summary.csv"
Q_ROUTES = EVIDENCE / "p_taucov_q_native_route_registry.csv"

OUT = EVIDENCE / "p_taucov_microscopic_residue_source_spec.csv"
SUMMARY = EVIDENCE / "p_taucov_microscopic_residue_source_spec_summary.csv"
DOC = DOCS / "p_taucov_microscopic_residue_source_spec.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SPEC_ID = "P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_v1"
STATUS = "P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_DEFINED_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "microscopic_residue_source_spec_no_object_no_scoring"


def main() -> int:
    if not SOURCE_GAP.exists():
        raise RuntimeError("Parent-source gap packet must exist before microscopic source spec.")
    gap = pd.read_csv(SOURCE_GAP).iloc[0]
    routes = pd.read_csv(Q_ROUTES) if Q_ROUTES.exists() else pd.DataFrame()

    rows = [
        {
            "SourceRouteID": "MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE",
            "ParentSelector": "compact-spectrum mode selection",
            "SourceExpression": "R_parent = Sum_{n in I_res} lambda_n |u_n><u_n| - Proj_smooth",
            "Primary": True,
            "WhyAdmissible": "directly targets non-smooth spectral residue and smooth-PSD exclusion",
            "RequiredBeforeObject": "declare operator, compact domain, eigenmode index set, smooth complement, normalization",
        },
        {
            "SourceRouteID": "MRS_ROUTE_B_BOUNDARY_DOMAIN_RESIDUE",
            "ParentSelector": "boundary/domain condition",
            "SourceExpression": "R_parent = B_boundary^T B_boundary - Proj_forbidden",
            "Primary": False,
            "WhyAdmissible": "can generate non-smooth boundary-localized structure before empirical bridge",
            "RequiredBeforeObject": "derive boundary operator from parent domain rather than data covariance",
        },
        {
            "SourceRouteID": "MRS_ROUTE_C_INDEX_RESIDUE",
            "ParentSelector": "index or protected-kernel residue",
            "SourceExpression": "R_parent = P_index H_parent P_index - Proj_smooth",
            "Primary": False,
            "WhyAdmissible": "would supply a protected, non-generic residue class",
            "RequiredBeforeObject": "declare index projector and prove target-blind protected subspace",
        },
        {
            "SourceRouteID": "MRS_ROUTE_D_PARENT_ACTION_HESSIAN_RESIDUE",
            "ParentSelector": "microscopic parent-action Hessian",
            "SourceExpression": "R_parent = Hessian(S_parent)_red - Proj_forbidden - Proj_smooth",
            "Primary": False,
            "WhyAdmissible": "connects residue to action-level source rather than toy operator recipe",
            "RequiredBeforeObject": "declare S_parent normal form and reduce nuisance/gauge directions before bridge",
        },
    ]
    table = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SpecID": SPEC_ID,
                **row,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in rows
        ]
    )
    table.to_csv(OUT, index=False)

    q_route_count = len(routes)
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SpecID": SPEC_ID,
                "Status": STATUS,
                "SourceRoutesDefined": len(table),
                "PrimaryRoute": "MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE",
                "ParentSourceGapStatus": str(gap["Status"]),
                "ResidueNormBeforeNormalization": float(gap["ResidueNormBeforeNormalization"]),
                "ExpandedPrimaryMinusStrongestNull": float(gap["ExpandedPrimaryMinusStrongestNull"]),
                "RegisteredQNativeRoutesSeen": q_route_count,
                "NextAllowedArtifact": "p_taucov_compact_spectral_residue_source_v1_no_score_preflight",
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Microscopic Residue Source Specification",
                "",
                f"Status: `{STATUS}`",
                "",
                "This is a no-score source specification. It exists because the previous",
                "parent-Hessian residue candidate collapsed to numerical zero after",
                "smooth-PSD, projection-null, and balance cleaning.",
                "",
                "## Source Requirement",
                "",
                "A future candidate must be selected upstream of the empirical bridge by a",
                "microscopic parent source selector. It cannot be another empirical",
                "covariance shape.",
                "",
                "## Declared Routes",
                "",
                "| Route | Selector | Primary |",
                "|---|---|---|",
                *[
                    f"| `{row['SourceRouteID']}` | {row['ParentSelector']} | `{row['Primary']}` |"
                    for row in rows
                ],
                "",
                "The first route to try is:",
                "",
                "`MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE`",
                "",
                "because it directly targets the current blocker: the need for a non-smooth",
                "spectral residue that generic smooth PSD covariance cannot reproduce.",
                "",
                "## Required Before Any Object",
                "",
                "- declare the parent operator or action source;",
                "- declare the compact domain or boundary condition;",
                "- declare the spectral/index/boundary residue selector;",
                "- declare the smooth complement to be excluded;",
                "- declare projection-null and gauge exclusion before empirical bridge;",
                "- freeze all thresholds before scoring;",
                "- use no target residuals, OOS scores, alpha behavior, or winning nulls to",
                "  choose the object.",
                "",
                "## Forbidden Claim",
                "",
                "> The source specification produces a Tau Core signal.",
                "",
                "## Allowed Claim",
                "",
                "> The source specification defines which microscopic parent-source routes",
                "> are admissible after the parent-source gap failure.",
                "",
                "## Next Allowed Artifact",
                "",
                "`p_taucov_compact_spectral_residue_source_v1_no_score_preflight`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
