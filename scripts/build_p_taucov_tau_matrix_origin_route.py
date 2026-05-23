#!/usr/bin/env python3
"""Build the Tau-theory matrix-origin route for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_tau_matrix_origin_route.md"
OUT_CSV = EVIDENCE / "p_taucov_tau_matrix_origin_route.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tau_matrix_origin_route_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
ROUTE_ID = "P_TAUCOV_TAU_MATRIX_ORIGIN_ROUTE_v1"
CLAIM_BOUNDARY = "tau_matrix_origin_route_theory_spec_no_concrete_packet"

ROWS = [
    {
        "ObjectID": "L0_B",
        "TauOrigin": "second variation / reduced Hessian of branch sector around B_*(Phi)",
        "FormalRoute": "L0_B = P_red D_B F_B|_(Phi,B_*) P_red",
        "StillMissing": "explicit F_B and branch-domain projector",
    },
    {
        "ObjectID": "R_B",
        "TauOrigin": "cross-response of branch equation to parent perturbation",
        "FormalRoute": "R_B = - P_red D_Phi F_B|_(Phi,B_*)",
        "StillMissing": "explicit D_Phi F_B from parent perturbation coupling",
    },
    {
        "ObjectID": "P_red",
        "TauOrigin": "admissible reduced branch domain after removing null/gauge/leakage modes",
        "FormalRoute": "P_red = I - P_null - P_gauge - P_forbidden",
        "StillMissing": "declared null/gauge mode basis",
    },
    {
        "ObjectID": "A_Phi",
        "TauOrigin": "direct parent morphology derivative",
        "FormalRoute": "A_Phi = D_Phi M_parent|_(Phi,B_*)",
        "StillMissing": "explicit M_parent",
    },
    {
        "ObjectID": "A_B",
        "TauOrigin": "branch contribution to morphology",
        "FormalRoute": "A_B = D_B M_parent|_(Phi,B_*)",
        "StillMissing": "explicit M_parent",
    },
    {
        "ObjectID": "P0",
        "TauOrigin": "fixed morphology projection at epsilon_P=0",
        "FormalRoute": "P0 = P_morph(Phi_0,B_*(Phi_0)) or declared coordinate projection",
        "StillMissing": "explicit P_morph and reference state",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RouteID": ROUTE_ID,
                **row,
                "ConcreteMatrixPresent": False,
                "CanEnterLinearPacket": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "RouteID": ROUTE_ID,
                "ObjectsRouted": len(df),
                "ConcreteMatricesPresent": 0,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "PrimaryMissingObject": "explicit_F_B_and_M_parent_and_P_morph",
                "NextStep": "derive_or_declare_F_B_M_parent_P_morph_target_blind",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Tau Matrix-Origin Route

Status: theory-origin route / no concrete packet / no metric evaluation / no
scoring authorization.

This document states how the required linear packet matrices must arise from
the Tau-side response model. It does not provide the matrices themselves.

## Origin Routes

| Matrix | Tau-side origin | Formal route |
| --- | --- | --- |
| `L0_B` | reduced branch Hessian / branch-sector linearization | `L0_B = P_red D_B F_B|_(Phi,B_*) P_red` |
| `R_B` | parent-to-branch forcing | `R_B = - P_red D_Phi F_B|_(Phi,B_*)` |
| `P_red` | reduced admissible branch domain | `P_red = I - P_null - P_gauge - P_forbidden` |
| `A_Phi` | direct parent morphology derivative | `A_Phi = D_Phi M_parent|_(Phi,B_*)` |
| `A_B` | branch morphology derivative | `A_B = D_B M_parent|_(Phi,B_*)` |
| `P0` | fixed morphology projection | `P0 = P_morph(Phi_0,B_*(Phi_0))` or declared coordinate projection |

## What This Achieves

This route prevents the matrices from being arbitrary. They are not fit
parameters and not score-selected kernels. They must be derivatives or
projections of declared Tau-side objects.

## What Is Still Missing

The route still requires explicit, target-blind definitions of:

```text
F_B
M_parent
P_morph
branch null/gauge basis
reference state Phi_0
```

Without those objects, no concrete matrix packet is authorized.

## Claim Boundary

Allowed statement:

```text
The linear packet matrices now have a declared Tau-side origin route.
```

Forbidden statement:

```text
The linear packet matrices have been derived or frozen.
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
