#!/usr/bin/env python3
"""Freeze the next P-TauCov minimal nonzero route after strict-linear failure."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_minimal_nonzero_route_freeze.md"
CSV = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze.csv"
SUMMARY = ROOT / "evidence/p_taucov_minimal_nonzero_route_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_MINIMAL_NONZERO_ROUTE_FREEZE_v1"
CLAIM_BOUNDARY = "minimal_nonzero_route_frozen_no_operator_no_scoring"


ROWS = [
    {
        "RouteID": "EPSILON_P_PROJECTION_RESPONSE_PRIMARY",
        "Role": "primary_next_model_family",
        "FrozenDecision": True,
        "Reason": "strict-linear failure is a projection-commuting cancellation; the minimal Tau-specific repair is a target-blind projection-response perturbation",
        "RequiredNextObject": "P1_projection_response_operator",
        "CanRescueStrictLinearAfterScore": False,
        "PTauCovScoringAuthorized": False,
    },
    {
        "RouteID": "LAMBDA_B_BRANCH_BACKREACTION_RESERVED",
        "Role": "reserved_control_or_future_family",
        "FrozenDecision": False,
        "Reason": "branch backreaction can be physically meaningful but is less diagnostic of the projection-specific failure mode without an independently derived branch operator",
        "RequiredNextObject": "B1_branch_backreaction_operator",
        "CanRescueStrictLinearAfterScore": False,
        "PTauCovScoringAuthorized": False,
    },
]


def main() -> int:
    DOC.parent.mkdir(exist_ok=True)
    CSV.parent.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "OutcomeInformationUsed": False,
                "ResidualInformationUsed": False,
                "ScoreInformationUsed": False,
                "P5CV3OutcomeUsed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in ROWS
        ]
    )
    df.to_csv(CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "StrictLinearStatus": "FAIL_STRICT_LINEAR_REJECTED",
                "FrozenPrimaryRoute": "EPSILON_P_PROJECTION_RESPONSE_PRIMARY",
                "ReservedRoute": "LAMBDA_B_BRANCH_BACKREACTION_RESERVED",
                "ProjectionOperatorPacketReady": False,
                "LinearCandidateFrozen": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "derive_target_blind_P1_projection_response_operator",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Minimal Nonzero Route Freeze

Status: next-route freeze / no projection-response operator yet / no scoring
authorization.

The strict-linear candidate failed the target-blind specificity audit because
the direct morphology term and the branch-mediated term cancel:

```text
T_tau = A_Phi + A_B L0_B^+ R_B = 0
```

This is not a positive Tau result. It is a useful negative gate: the
strict-linear model is too degenerate to freeze.

## Frozen Next Route

Primary next route:

```text
epsilon_P projection-response perturbation
```

Reserved route:

```text
lambda_B branch-backreaction perturbation
```

The reason for choosing `epsilon_P` first is target-blind and structural. The
failed strict-linear model collapses because all active maps reduce to the same
commuting reduced-domain projector. A projection-response perturbation is the
minimal way to test whether Tau-specific structure enters through the
observer/projection map rather than through generic branch covariance freedom.

## Required Next Object

Before any score can be computed, the program must derive a concrete
target-blind operator:

```text
P1_projection_response_operator
```

It must be built from declared Tau-side/projection-side rules only. It must not
use target residuals, P5C v3 outcomes, family-localized score behavior, or
post-scoring tuning.

## Claim Boundary

Allowed statement:

```text
The next P-TauCov model-family route is frozen as epsilon_P-first after the
strict-linear negative gate.
```

Forbidden statement:

```text
The epsilon_P route has produced a Tau signal or is authorized for empirical
P-TauCov scoring.
```
""",
        encoding="utf-8",
    )

    for path in [DOC, CSV, SUMMARY]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
