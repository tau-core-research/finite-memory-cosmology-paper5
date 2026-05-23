#!/usr/bin/env python3
"""Build the P-TauCov coordinate-basis source-candidate audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_coordinate_basis_source_candidates.md"
OUT_CSV = EVIDENCE / "p_taucov_coordinate_basis_source_candidates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_coordinate_basis_source_candidates_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_COORDINATE_BASIS_SOURCE_CANDIDATES_v1"
CLAIM_BOUNDARY = "source_candidates_declared_no_basis_packet"

ROWS = [
    {
        "CandidateSource": "TauSideSymbolicDefinition",
        "BasisContribution": "abstract Phi, B, morphology, and projection axes from the Tau-side definition spec",
        "AllowedForCandidateBasis": True,
        "Reason": "theory-declared and target-blind, but still needs finite-dimensional realization",
        "RequiredNextArtifact": "finite_dimensional_symbolic_axis_map",
    },
    {
        "CandidateSource": "CoordinateConventionOnly",
        "BasisContribution": "origin, center, units, and scale conventions",
        "AllowedForCandidateBasis": True,
        "Reason": "allowed if declared before residual or score inspection",
        "RequiredNextArtifact": "coordinate_convention_manifest",
    },
    {
        "CandidateSource": "PublishedExternalMetadata",
        "BasisContribution": "citable non-outcome metadata such as source families or observing-context tags",
        "AllowedForCandidateBasis": True,
        "Reason": "allowed only if not selected from P5C v3 score behavior",
        "RequiredNextArtifact": "source_citation_and_no_score_selection_audit",
    },
    {
        "CandidateSource": "ExistingP5CKernelV3Gains",
        "BasisContribution": "family gains, local covariance gains, OOS score patterns",
        "AllowedForCandidateBasis": False,
        "Reason": "would leak scored anomaly structure into the Tau candidate basis",
        "RequiredNextArtifact": "forbidden_source_record_only",
    },
    {
        "CandidateSource": "HeldOutResidualsOrTargets",
        "BasisContribution": "target residual signs, magnitudes, or covariance alignment after scoring",
        "AllowedForCandidateBasis": False,
        "Reason": "direct outcome leakage",
        "RequiredNextArtifact": "forbidden_source_record_only",
    },
    {
        "CandidateSource": "PostHocFamilyLocalization",
        "BasisContribution": "basis axes selected because a family looked strong or weak after scoring",
        "AllowedForCandidateBasis": False,
        "Reason": "turns branch localization into hidden model selection",
        "RequiredNextArtifact": "forbidden_source_record_only",
    },
    {
        "CandidateSource": "GenericSmoothNullTemplates",
        "BasisContribution": "generic smooth PSD or low-rank templates",
        "AllowedForCandidateBasis": False,
        "Reason": "can be used as null comparators, not as Tau candidate source",
        "RequiredNextArtifact": "null_comparator_registry_only",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                **row,
                "ConcreteBasisRowsProvided": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    allowed = int(df["AllowedForCandidateBasis"].astype(bool).sum())
    forbidden = int((~df["AllowedForCandidateBasis"].astype(bool)).sum())
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "SourcesAudited": len(df),
                "AllowedCandidateSources": allowed,
                "ForbiddenCandidateSources": forbidden,
                "ConcreteBasisRowsProvided": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "build_finite_dimensional_symbolic_axis_map_from_allowed_sources",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Coordinate-Basis Source Candidates

Status: source-candidate audit / no concrete basis rows / no coordinate-basis
packet / no reference-domain selection / no metric evaluation / no scoring
authorization.

The coordinate-basis packet gate says what a concrete basis must contain. This
audit says which source classes may feed that basis.

## Allowed Source Classes

| Source | Use | Condition |
| --- | --- | --- |
| Tau-side symbolic definition | Defines abstract `Phi`, `B`, morphology, and projection axes. | Must be converted into a finite-dimensional axis map before use. |
| Coordinate convention only | Defines origin, center, units, and scale conventions. | Must be declared before residual or score inspection. |
| Published external metadata | Defines citable non-outcome families or observing-context tags. | Must not be selected from P5C v3 score behavior. |

## Forbidden Source Classes

| Source | Why forbidden |
| --- | --- |
| Existing P5C v3 gains | Would leak scored anomaly structure into the Tau candidate basis. |
| Held-out residuals or targets | Direct outcome leakage. |
| Post-hoc family localization | Turns branch localization into hidden model selection. |
| Generic smooth null templates | Allowed as null comparators only, not Tau candidate basis. |

## Consequence

The next artifact must be a finite-dimensional symbolic axis map built from the
allowed source classes only. It may describe candidate axes, but it still must
not create matrices, evaluate metrics, or authorize scoring.

## Claim Boundary

Allowed statement:

```text
Allowed and forbidden source classes for the coordinate basis are declared.
```

Forbidden statement:

```text
A concrete coordinate-basis packet has been built or accepted.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
