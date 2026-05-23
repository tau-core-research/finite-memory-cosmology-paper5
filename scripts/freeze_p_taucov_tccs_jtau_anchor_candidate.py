#!/usr/bin/env python3
"""Freeze a target-blind J_tau anchor candidate for TCCS."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/p_taucov/linear"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

COORDINATES = DATA / "coordinate_basis.csv"
OUT_MATRIX = EVIDENCE / "p_taucov_tccs_jtau_anchor_candidate_matrix.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_jtau_anchor_candidate_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_jtau_anchor_candidate.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_v1"
ANCHOR_ID = "JTAU_A_PARENT_COMPLEX_STRUCTURE"
STATUS = "P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_FROZEN_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_jtau_anchor_candidate_frozen_no_object_no_scoring"

PAIR_RULES = [
    ("TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE", "parent_source_to_branch_response"),
    ("TEMPLATE_M_PARENT_MORPHOLOGY", "TEMPLATE_P_MORPH_PROJECTION", "morphology_to_projection_readout"),
]


def main() -> int:
    coords = pd.read_csv(COORDINATES)
    ids = list(coords["coordinate_id"].astype(str))
    idx = {coordinate_id: i for i, coordinate_id in enumerate(ids)}
    j = np.zeros((len(ids), len(ids)), dtype=float)
    for left, right, _ in PAIR_RULES:
        if left not in idx or right not in idx:
            raise ValueError(f"missing coordinate pair: {left}, {right}")
        i, k = idx[left], idx[right]
        j[i, k] = 1.0
        j[k, i] = -1.0
    pd.DataFrame(j, columns=ids).assign(coordinate_id=ids)[["coordinate_id", *ids]].to_csv(OUT_MATRIX, index=False)

    skew_error = float(np.max(np.abs(j + j.T)))
    trace = float(np.trace(j))
    frob = float(np.linalg.norm(j))
    active_axes = int(np.count_nonzero(np.linalg.norm(j, axis=0) + np.linalg.norm(j, axis=1)))
    rank = int(np.linalg.matrix_rank(j))
    pair_text = "; ".join(f"{left}->{right} ({reason})" for left, right, reason in PAIR_RULES)

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "AnchorID": ANCHOR_ID,
                "Status": STATUS,
                "CoordinateSource": str(COORDINATES.relative_to(ROOT)),
                "PairRules": pair_text,
                "SkewSymmetryMaxError": skew_error,
                "Trace": trace,
                "FrobeniusNorm": frob,
                "Rank": rank,
                "ActiveAxes": active_axes,
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "UsesDominantFamilyIdentity": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        f"""# P-TauCov TCCS J_tau Anchor Candidate

Freeze ID: `P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_v1`

Status:

`{STATUS}`

## Anchor

Selected candidate class:

```text
{ANCHOR_ID}
```

The anchor is a fixed skew parent-coordinate orientation on the frozen linear coordinate basis:

```text
Phi -> B
M   -> P
```

where:

- `Phi` is the parent source coordinate;
- `B` is the branch response coordinate;
- `M` is the parent morphology coordinate;
- `P` is the morphology/projection readout coordinate.

The matrix is antisymmetric by construction:

```text
J_tau^T = -J_tau
```

## Why This Is Target-Blind

The pair ordering is inherited from the Tau-side symbolic coordinate packet and the projection-essential parent-action normal-form route. It does not use:

- target residuals;
- empirical score signs;
- P5C gains;
- dominant family identity;
- post-score sign flipping.

## What This Does Not Authorize

This file does not build the TCCS object. It does not compute an orientation margin. It does not authorize scoring.

The next required gate is a pre-score validation that this `J_tau` candidate can orient a projection-orthogonal, branch-balanced commutator without collapsing into projection-null, morphology-null, diagonal, or family-localized structure.

## Diagnostics

| Quantity | Value |
|---|---:|
| skew-symmetry max error | `{skew_error}` |
| trace | `{trace}` |
| Frobenius norm | `{frob}` |
| rank | `{rank}` |
| active axes | `{active_axes}` |

## Claim Boundary

Allowed statement:

> A target-blind parent-coordinate orientation anchor candidate has been frozen for the TCCS route.

Forbidden statement:

> The anchor has oriented a valid TCCS object, authorized scoring, or produced a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
