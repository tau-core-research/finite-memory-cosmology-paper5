#!/usr/bin/env python3
"""Build the P-TauCov minimal linear-source convention freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_source_convention_freeze.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_source_convention_freeze.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_source_convention_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_LINEAR_SOURCE_CONVENTION_FREEZE_v1"
CLAIM_BOUNDARY = "linear_source_conventions_frozen_no_source_packet"

ROWS = [
    {
        "SourceObject": "K_B",
        "Convention": "identity_on_retained_reduced_domain",
        "Rationale": "minimal positive branch Hessian on P_red-retained coordinates",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "Gamma_B",
        "Convention": "zero_regularizer",
        "Rationale": "no extra damping unless separately justified before metric evaluation",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "D_Phi_K_B",
        "Convention": "zero_derivative",
        "Rationale": "strict linear baseline has no parent-dependent Hessian deformation",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "D_Phi_J_B",
        "Convention": "identity_parent_to_branch_on_shared_retained_axes",
        "Rationale": "minimal branch forcing from shared retained parent/branch coordinate axes",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "G_Phi",
        "Convention": "identity_parent_to_morphology_on_shared_retained_axes",
        "Rationale": "minimal direct morphology carrier baseline",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "G_B",
        "Convention": "identity_branch_to_morphology_on_shared_retained_axes",
        "Rationale": "minimal branch morphology carrier baseline",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
    {
        "SourceObject": "P0_SOURCE",
        "Convention": "identity_on_retained_morphology_coordinates",
        "Rationale": "fixed coordinate projection baseline before any projection-response model",
        "PacketStatus": "MAY_SUPPLY_MINIMAL_BASELINE_SOURCE",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **row,
                "ConcreteSourceSupplied": False,
                "LinearObjectsDerivable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
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
                "FreezeID": FREEZE_ID,
                "ConventionsFrozen": len(df),
                "ConcreteSourcesSupplied": False,
                "LinearObjectsDerivable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "build_minimal_target_blind_linear_source_packet",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Minimal Linear-Source Convention Freeze

Status: source-convention freeze / no concrete source matrices / no derived
linear objects / no metric evaluation / no scoring authorization.

This artifact freezes the minimal target-blind source conventions that may be
used to build a first finite-dimensional source packet. These conventions are
baseline choices, not empirical evidence and not a Tau signal.

## Frozen Minimal Conventions

| Source object | Convention |
| --- | --- |
| `K_B` | identity on retained reduced-domain coordinates |
| `Gamma_B` | zero regularizer |
| `D_Phi_K_B` | zero derivative |
| `D_Phi_J_B` | identity parent-to-branch on shared retained axes |
| `G_Phi` | identity parent-to-morphology on shared retained axes |
| `G_B` | identity branch-to-morphology on shared retained axes |
| `P0_SOURCE` | identity on retained morphology coordinates |

## Guardrail

The minimal source packet built from these conventions is allowed only as a
target-blind baseline source packet. It must not be interpreted as a positive
P-TauCov result, and it must not be tuned after any metric or score is seen.

## Claim Boundary

Allowed statement:

```text
Minimal target-blind linear-source conventions are frozen.
```

Forbidden statement:

```text
Concrete source matrices, derived linear objects, covariance response, or
P-TauCov score are available.
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
