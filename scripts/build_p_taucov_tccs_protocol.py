#!/usr/bin/env python3
"""Build the Tau Commutator Curvature Signature protocol spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_GATES = ROOT / "evidence/p_taucov_tccs_protocol_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_tccs_protocol_summary.csv"
OUT_DOC = ROOT / "docs/p_taucov_tccs_protocol.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_PROTOCOL_v1"
STATUS = "P_TAUCOV_TCCS_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_protocol_defined_no_object_no_scoring"


GATES = [
    (
        "TCCS-G1_PARENT_HESSIAN_SOURCE",
        "L_B_red must be declared as a parent-side reduced Hessian or response operator before any score access.",
        "required",
    ),
    (
        "TCCS-G2_COMMUTATOR_OBJECT",
        "The primary object must be based on [L_B_red, P_morph], not on a direct morphology/projection shape.",
        "required",
    ),
    (
        "TCCS-G3_PROJECTION_ORTHOGONALITY",
        "Projection-null overlap after Pi_perp projection must remain below the frozen threshold.",
        "<=0.50",
    ),
    (
        "TCCS-G4_MORPHOLOGY_ORTHOGONALITY",
        "Morphology-null overlap after Pi_perp projection must remain below the frozen threshold.",
        "<=0.50",
    ),
    (
        "TCCS-G5_BALANCE_RETENTION",
        "Pi_bal projection must retain nontrivial norm while removing family/clock nuisance directions.",
        "retention>=0.20 and leakage<1e-10",
    ),
    (
        "TCCS-G6_FAMILY_BALANCE",
        "No family may dominate pre-score energy or positive capacity.",
        "max_family_energy_share<=0.50",
    ),
    (
        "TCCS-G7_DIAGONAL_CONTROL",
        "Diagonal energy must be absent or explicitly excluded from the signed statistic.",
        "diagonal_share<=0.10",
    ),
    (
        "TCCS-G8_ORIENTATION_ANCHOR",
        "A target-blind parent-side orientation anchor J_tau must fix the sign before scoring.",
        "orientation_margin>0",
    ),
    (
        "TCCS-G9_SIGN_FLIP_NOT_EQUIVALENT",
        "The sign-flip control must remain an orientation control, not an alternative survival route.",
        "required",
    ),
    (
        "TCCS-G10_TARGET_BLINDNESS",
        "No target residuals, score outcomes, P5C gains, or dominant-family identities may enter construction.",
        "required",
    ),
]


def main() -> int:
    gate_rows = [
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "GateID": gate_id,
            "Requirement": requirement,
            "Threshold": threshold,
            "ScoringAuthorizedByGate": False,
            "ClaimBoundary": CLAIM_BOUNDARY,
        }
        for gate_id, requirement, threshold in GATES
    ]
    pd.DataFrame(gate_rows).to_csv(OUT_GATES, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "ShortName": "TCCS",
                "LongName": "Tau Commutator Curvature Signature",
                "FormalObject": "T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)",
                "Gates": len(GATES),
                "ObjectConstructed": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)
    OUT_DOC.write_text(
        """# P-TauCov TCCS Protocol

Freeze ID: `P_TAUCOV_TCCS_PROTOCOL_v1`

Status:

`P_TAUCOV_TCCS_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING`

## Name

Short name:

```text
TCCS
```

Long name:

```text
Tau Commutator Curvature Signature
```

Formal reading:

```text
oriented reduced parent-Hessian commutator signature
```

## Motivation

The previous P-TauCov ladder produced a useful negative-control result. Direct shape, covariance, diagonal-orthogonal, and P3 balanced candidates did not produce a surviving Tau-specific empirical signal.

The failure pattern suggests that the next Tau-side object should not be another shape or covariance kernel. It should test whether the parent-side branch response fails to commute with the morphology/projection readout.

## Candidate Class

The intended object class is:

```text
C_tau = [L_B_red, P_morph] = L_B_red P_morph - P_morph L_B_red
```

The scoreable form, if it ever passes pre-score gates, is:

```text
T_tau = Normalize(
  Pi_bal
  Pi_perp
  Orient_+([L_B_red, P_morph]; J_tau)
  Pi_perp
  Pi_bal
)
```

where:

- `L_B_red` is a target-blind reduced parent-Hessian or response operator;
- `P_morph` is the morphology/projection readout operator;
- `Pi_perp` removes projection-null and morphology-null directions;
- `Pi_bal` removes family/clock nuisance directions;
- `J_tau` is a target-blind parent-side orientation anchor;
- `Orient_+` rejects the object if the orientation margin is not positive.

## Required Gates

| Gate | Requirement | Threshold |
|---|---|---|
| `TCCS-G1` | parent Hessian source declared before score access | required |
| `TCCS-G2` | object is a commutator, not direct shape | required |
| `TCCS-G3` | projection-null overlap after orthogonalization | `<=0.50` |
| `TCCS-G4` | morphology-null overlap after orthogonalization | `<=0.50` |
| `TCCS-G5` | balance retention and leakage | `retention>=0.20`, `leakage<1e-10` |
| `TCCS-G6` | family balance | `max_family_energy_share<=0.50` |
| `TCCS-G7` | diagonal control | `diagonal_share<=0.10` |
| `TCCS-G8` | parent orientation anchor | `orientation_margin>0` |
| `TCCS-G9` | sign-flip not promoted to survival | required |
| `TCCS-G10` | target blindness | required |

## Forbidden Moves

- Do not choose the sign from empirical score behavior.
- Do not use the previous strongest family-clock cell as a template.
- Do not treat PSD projection as primary unless orientation retention is separately frozen and passes.
- Do not report signed diagnostic success as covariance survival.
- Do not call this Tau Core validation without a frozen held-out scorecard pass.

## Claim Boundary

Allowed statement:

> TCCS is a proposed next Tau-side observable class designed to avoid the failure modes exposed by the P3 balanced scorecard.

Forbidden statement:

> TCCS has produced a Tau signal, survived empirical scoring, or validated Tau Core.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
