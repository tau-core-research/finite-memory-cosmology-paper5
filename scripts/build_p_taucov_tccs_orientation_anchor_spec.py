#!/usr/bin/env python3
"""Build the target-blind orientation-anchor spec for TCCS."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

OUT_CANDIDATES = EVIDENCE / "p_taucov_tccs_orientation_anchor_candidates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_orientation_anchor_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_orientation_anchor_spec.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_v1"
STATUS = "P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_DEFINED_NO_ANCHOR_FROZEN"
CLAIM_BOUNDARY = "tccs_orientation_anchor_spec_no_anchor_no_scoring"


CANDIDATES = [
    {
        "AnchorID": "JTAU_A_PARENT_COMPLEX_STRUCTURE",
        "Definition": "J_tau is the fixed skew/complex structure of the parent reduced branch coordinates.",
        "AllowedSource": "target-blind parent coordinate packet or compact-cell orientation convention",
        "ForbiddenSource": "empirical residual sign, score sign, dominant family, or post-score flip",
        "CurrentStatus": "SOURCE_NOT_FROZEN",
        "CanFreezeNow": False,
    },
    {
        "AnchorID": "JTAU_B_BRANCH_ORDER_ORIENTATION",
        "Definition": "J_tau is induced by the declared ordered branch-response basis and its orientation form.",
        "AllowedSource": "frozen branch basis order plus determinant/orientation convention",
        "ForbiddenSource": "choosing the branch order that maximizes signed statistic",
        "CurrentStatus": "SOURCE_NOT_FROZEN",
        "CanFreezeNow": False,
    },
    {
        "AnchorID": "JTAU_C_HESSIAN_SKEW_PAIRING",
        "Definition": "J_tau is the antisymmetric pairing associated with the reduced parent Hessian block decomposition.",
        "AllowedSource": "declared Hessian block algebra before object construction",
        "ForbiddenSource": "P5C gains or P-TauCov scorecard outcomes",
        "CurrentStatus": "SOURCE_NOT_FROZEN",
        "CanFreezeNow": False,
    },
]


def main() -> int:
    rows = []
    for candidate in CANDIDATES:
        rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **candidate,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(rows).to_csv(OUT_CANDIDATES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "CandidateAnchors": len(CANDIDATES),
                "FrozenAnchorCount": 0,
                "AnchorSelected": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        """# P-TauCov TCCS Orientation Anchor Spec

Freeze ID: `P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_v1`

Status:

`P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_DEFINED_NO_ANCHOR_FROZEN`

## Purpose

The TCCS object is signed:

```text
Orient_+([L_B_red, P_morph]; J_tau)
```

Therefore the sign must be fixed by a target-blind parent-side orientation anchor, not by empirical score behavior.

## Candidate Anchor Classes

| Anchor | Meaning | Current status |
|---|---|---|
| `JTAU_A_PARENT_COMPLEX_STRUCTURE` | fixed skew/complex structure of the reduced parent coordinates | `SOURCE_NOT_FROZEN` |
| `JTAU_B_BRANCH_ORDER_ORIENTATION` | orientation induced by the declared branch basis order | `SOURCE_NOT_FROZEN` |
| `JTAU_C_HESSIAN_SKEW_PAIRING` | antisymmetric pairing from the reduced Hessian block algebra | `SOURCE_NOT_FROZEN` |

## Freeze Rule

An anchor may be frozen only if all of the following are true:

1. its source exists before TCCS object construction;
2. its sign convention is independent of target residuals and empirical score signs;
3. it does not use the dominant family or clock cell identified by previous failed scorecards;
4. the anchor is a parent-side convention, not a data-fit convention;
5. the selected anchor is recorded before any orientation-margin or scorecard result is viewed.

## Forbidden Moves

- Do not flip the commutator sign after seeing alignment.
- Do not choose between anchor candidates after comparing score outcomes.
- Do not use the previous sign-flip control as a positive result.
- Do not promote a signed diagnostic if the primary frozen route fails.

## Claim Boundary

Allowed statement:

> The TCCS orientation-anchor spec defines what a valid target-blind sign convention would require.

Forbidden statement:

> A TCCS orientation anchor has already been selected, frozen, or empirically validated.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
