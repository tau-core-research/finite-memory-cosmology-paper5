#!/usr/bin/env python3
"""Build the target-blind Tau-side definition spec for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_tau_side_definition_spec.md"
OUT_CSV = EVIDENCE / "p_taucov_tau_side_definition_spec.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tau_side_definition_spec_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SPEC_ID = "P_TAUCOV_TAU_SIDE_DEFINITION_SPEC_v1"
CLAIM_BOUNDARY = "tau_side_definition_spec_no_concrete_packet_no_scoring"

ROWS = [
    {
        "ObjectID": "F_B",
        "DefinitionStatus": "CANDIDATE_FORM_DECLARED_NOT_FROZEN",
        "CandidateDefinition": "F_B(Phi,B)=Grad_B U_branch(B;Phi)+Gamma_B B",
        "TauRole": "branch stationarity / relaxation equation",
        "LinearDerivativeProduced": "D_B F_B and D_Phi F_B",
    },
    {
        "ObjectID": "U_branch",
        "DefinitionStatus": "CANDIDATE_FORM_DECLARED_NOT_FROZEN",
        "CandidateDefinition": "U_branch(B;Phi)=1/2 <B,K_B(Phi)B> - <J_B(Phi),B>",
        "TauRole": "target-blind branch potential generating relaxation and forcing",
        "LinearDerivativeProduced": "K_B and D_Phi J_B minus D_Phi K_B terms",
    },
    {
        "ObjectID": "M_parent",
        "DefinitionStatus": "CANDIDATE_FORM_DECLARED_NOT_FROZEN",
        "CandidateDefinition": "M_parent(Phi,B)=M0 + G_Phi Phi + G_B B",
        "TauRole": "minimal observable morphology carrier",
        "LinearDerivativeProduced": "D_Phi M_parent and D_B M_parent",
    },
    {
        "ObjectID": "P_morph",
        "DefinitionStatus": "CANDIDATE_FORM_DECLARED_NOT_FROZEN",
        "CandidateDefinition": "P_morph(Phi,B)=P0 at epsilon_P=0",
        "TauRole": "fixed projection/observable coordinate map for strictly linear candidate",
        "LinearDerivativeProduced": "P0; no projection derivative in strict linear pass",
    },
    {
        "ObjectID": "Phi_0",
        "DefinitionStatus": "REFERENCE_REQUIRED_NOT_SET",
        "CandidateDefinition": "reference parent state selected before packet generation",
        "TauRole": "evaluation point for derivatives",
        "LinearDerivativeProduced": "freezes where derivatives are evaluated",
    },
    {
        "ObjectID": "NullGaugeBasis",
        "DefinitionStatus": "DOMAIN_REQUIRED_NOT_SET",
        "CandidateDefinition": "basis for null/gauge/forbidden modes excluded by P_red",
        "TauRole": "prevents singular inversion and hidden fitting",
        "LinearDerivativeProduced": "P_red",
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SpecID": SPEC_ID,
                **row,
                "ConcreteMatrixProduced": False,
                "CanEnterLinearPacket": False,
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
                "SpecID": SPEC_ID,
                "ObjectsSpecified": len(df),
                "ConcreteMatricesProduced": 0,
                "ReferenceStateSet": False,
                "NullGaugeBasisSet": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "freeze_reference_state_and_null_gauge_basis_then_derive_symbolic_linear_matrices",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Tau-Side Definition Spec

Status: candidate Tau-side definitions / not frozen / no concrete packet / no
metric evaluation / no scoring authorization.

This document gives the first explicit target-blind definitions for the
Tau-side objects required by the matrix-origin route:

```text
F_B
M_parent
P_morph
```

It still does not produce concrete matrices. It defines the symbolic origin from
which those matrices must later be derived.

## 1. Branch Equation

The branch equation is proposed as a stationarity/relaxation equation:

```math
F_B(\\Phi,B)
=
\\nabla_B U_{\\rm branch}(B;\\Phi)
+
\\Gamma_B B.
```

The branch potential is:

```math
U_{\\rm branch}(B;\\Phi)
=
\\frac{1}{2}\\langle B,K_B(\\Phi)B\\rangle
-
\\langle J_B(\\Phi),B\\rangle.
```

Therefore the linear packet objects must come from:

```math
D_B F_B = K_B(\\Phi_0)+\\Gamma_B,
```

and:

```math
D_\\Phi F_B[\\delta\\Phi]
=
\\frac{1}{2}\\langle B,D_\\Phi K_B[\\delta\\Phi]B\\rangle_B
-
D_\\Phi J_B[\\delta\\Phi].
```

The exact finite-dimensional representation of `K_B`, `J_B`, and `Gamma_B`
is not yet frozen.

## 2. Parent Morphology

The minimal morphology carrier is:

```math
M_{\\rm parent}(\\Phi,B)
=
M_0 + G_\\Phi\\Phi + G_B B.
```

Thus:

```math
A_\\Phi = D_\\Phi M_{\\rm parent}=G_\\Phi,
\\qquad
A_B = D_B M_{\\rm parent}=G_B.
```

`G_Phi` and `G_B` must be derived from a target-blind morphology definition or
frozen as a candidate morphology map before metric evaluation.

## 3. Projection Map

For the strictly linear candidate:

```math
P_{\\rm morph}(\\Phi,B)=P_0,
\\qquad
\\epsilon_P=0.
```

This means the first specificity audit tests branch relaxation under a fixed
projection map. A nonzero projection-response term `epsilon_P P_1(Phi,B)` is a
separate future model family and cannot rescue a failed strict-linear audit.

## 4. Remaining Required Freezes

The following are still missing:

```text
reference state Phi_0;
branch null/gauge/forbidden basis;
finite-dimensional K_B, J_B, Gamma_B;
target-blind G_Phi and G_B;
fixed P0.
```

## Claim Boundary

Allowed statement:

```text
The Tau-side objects now have explicit candidate symbolic definitions.
```

Forbidden statement:

```text
The Tau-side definitions have produced a valid linear packet or covariance
response.
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
