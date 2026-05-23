#!/usr/bin/env python3
"""Build the P-TauCov reference-state and reduced-domain freeze policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_reference_domain_freeze.md"
OUT_CSV = EVIDENCE / "p_taucov_reference_domain_freeze.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_reference_domain_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_REFERENCE_DOMAIN_FREEZE_v1"
CLAIM_BOUNDARY = "reference_domain_policy_no_concrete_basis_no_packet"

ROWS = [
    {
        "Item": "Phi_0",
        "Policy": "reference parent state must be selected from target-blind coordinate/source convention",
        "Status": "POLICY_DECLARED_VALUE_NOT_SET",
        "BlocksPacket": True,
    },
    {
        "Item": "B_star_at_Phi_0",
        "Policy": "branch stationary point must solve F_B(Phi_0,B)=0 under declared branch equation",
        "Status": "FORMULA_DECLARED_VALUE_NOT_SOLVED",
        "BlocksPacket": True,
    },
    {
        "Item": "P_null",
        "Policy": "null directions of L_B candidate must be declared before inversion",
        "Status": "POLICY_DECLARED_BASIS_NOT_SET",
        "BlocksPacket": True,
    },
    {
        "Item": "P_gauge",
        "Policy": "gauge-like or coordinate redundancy directions must be excluded before inversion",
        "Status": "POLICY_DECLARED_BASIS_NOT_SET",
        "BlocksPacket": True,
    },
    {
        "Item": "P_forbidden",
        "Policy": "outcome-derived directions are forbidden and projected out if present",
        "Status": "POLICY_DECLARED_BASIS_NOT_SET",
        "BlocksPacket": True,
    },
    {
        "Item": "P_red",
        "Policy": "P_red = I - P_null - P_gauge - P_forbidden after bases are frozen",
        "Status": "FORMULA_DECLARED_MATRIX_NOT_BUILT",
        "BlocksPacket": True,
    },
    {
        "Item": "InvertibilityAudit",
        "Policy": "L_B^red must be invertible or regularized by predeclared rule on P_red domain",
        "Status": "NOT_RUN",
        "BlocksPacket": True,
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
                "ConcreteValuePresent": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
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
                "FreezeID": FREEZE_ID,
                "ItemsDeclared": len(df),
                "ConcreteValuesPresent": 0,
                "ReferenceStateFrozen": False,
                "ReducedDomainFrozen": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_target_blind_phi0_and_null_gauge_basis",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Reference-State And Reduced-Domain Freeze

Status: freeze policy / no concrete reference state / no reduced-domain matrix /
no metric evaluation / no scoring authorization.

The Tau-side definition spec requires derivatives at a reference state and an
invertible reduced branch domain. This artifact declares the freeze policy for
those objects without yet supplying their concrete values.

## Required Reference Objects

| Item | Policy |
| --- | --- |
| `Phi_0` | Select from a target-blind coordinate/source convention. |
| `B_star(Phi_0)` | Solve `F_B(Phi_0,B)=0` under the declared branch equation. |
| `P_null` | Declare null directions before inversion. |
| `P_gauge` | Exclude gauge-like or coordinate redundancy directions. |
| `P_forbidden` | Exclude outcome-derived directions if present. |
| `P_red` | Build `P_red = I - P_null - P_gauge - P_forbidden`. |
| `InvertibilityAudit` | Verify or predeclare regularization of `L_B^red`. |

## Hard Rule

`Phi_0`, `P_null`, `P_gauge`, and `P_forbidden` must not be selected from:

```text
held-out residuals;
P5C v3 family gains;
OOS DeltaNLL pattern;
linear specificity metric pass/fail result;
post-hoc support localization.
```

## Claim Boundary

Allowed statement:

```text
The reference-state and reduced-domain freeze policy is declared.
```

Forbidden statement:

```text
The reference state or reduced branch domain is already frozen.
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
