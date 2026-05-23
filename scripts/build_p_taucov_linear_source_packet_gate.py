#!/usr/bin/env python3
"""Build the P-TauCov finite-dimensional linear-source packet gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_source_packet_gate.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_source_packet_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_source_packet_gate_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_LINEAR_SOURCE_PACKET_GATE_v1"
CLAIM_BOUNDARY = "linear_source_packet_gate_declared_no_source_objects"

ROWS = [
    {
        "SourceObject": "K_B",
        "Role": "branch potential Hessian component",
        "RequiredFor": "L0_B",
        "AllowedOrigin": "Tau-side branch potential definition or target-blind theory convention",
    },
    {
        "SourceObject": "Gamma_B",
        "Role": "branch relaxation/damping regularizer",
        "RequiredFor": "L0_B",
        "AllowedOrigin": "target-blind regularization convention declared before metric evaluation",
    },
    {
        "SourceObject": "D_Phi_K_B",
        "Role": "parent perturbation derivative of branch Hessian",
        "RequiredFor": "R_B",
        "AllowedOrigin": "Tau-side derivative definition; no residual or score fitting",
    },
    {
        "SourceObject": "D_Phi_J_B",
        "Role": "parent perturbation derivative of branch source term",
        "RequiredFor": "R_B",
        "AllowedOrigin": "Tau-side derivative definition; no residual or score fitting",
    },
    {
        "SourceObject": "G_Phi",
        "Role": "direct parent morphology derivative",
        "RequiredFor": "A_Phi",
        "AllowedOrigin": "target-blind morphology definition",
    },
    {
        "SourceObject": "G_B",
        "Role": "branch morphology derivative",
        "RequiredFor": "A_B",
        "AllowedOrigin": "target-blind morphology definition",
    },
    {
        "SourceObject": "P0_SOURCE",
        "Role": "fixed morphology projection source",
        "RequiredFor": "P0",
        "AllowedOrigin": "declared coordinate projection or target-blind P_morph definition",
    },
]

REQUIRED_PACKET_FILES = [
    "data/p_taucov/linear/source/K_B.csv",
    "data/p_taucov/linear/source/Gamma_B.csv",
    "data/p_taucov/linear/source/D_Phi_K_B.csv",
    "data/p_taucov/linear/source/D_Phi_J_B.csv",
    "data/p_taucov/linear/source/G_Phi.csv",
    "data/p_taucov/linear/source/G_B.csv",
    "data/p_taucov/linear/source/P0_source.csv",
    "evidence/p_taucov_linear_source_manifest.yaml",
    "evidence/p_taucov_linear_source.sha256",
    "evidence/p_taucov_linear_source_leakage_audit.csv",
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GateID": GATE_ID,
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
                "GateID": GATE_ID,
                "SourceObjectsDeclared": len(df),
                "RequiredPacketFiles": len(REQUIRED_PACKET_FILES),
                "LinearSourceGateDeclared": True,
                "ConcreteSourcesSupplied": False,
                "LinearObjectsDerivable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_target_blind_finite_dimensional_source_objects",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Finite-Dimensional Linear-Source Packet Gate

Status: source gate / no concrete source matrices / no linear objects / no
metric evaluation / no scoring authorization.

This gate specifies the finite-dimensional source objects required before the
linear matrices `L0_B`, `R_B`, `A_Phi`, `A_B`, and `P0` can be derived.

## Required Source Objects

| Source object | Role | Required for |
| --- | --- | --- |
| `K_B` | Branch potential Hessian component. | `L0_B` |
| `Gamma_B` | Branch relaxation/damping regularizer. | `L0_B` |
| `D_Phi_K_B` | Parent derivative of branch Hessian. | `R_B` |
| `D_Phi_J_B` | Parent derivative of branch source term. | `R_B` |
| `G_Phi` | Direct parent morphology derivative. | `A_Phi` |
| `G_B` | Branch morphology derivative. | `A_B` |
| `P0_SOURCE` | Fixed morphology projection source. | `P0` |

## Required Packet Files

```text
data/p_taucov/linear/source/K_B.csv
data/p_taucov/linear/source/Gamma_B.csv
data/p_taucov/linear/source/D_Phi_K_B.csv
data/p_taucov/linear/source/D_Phi_J_B.csv
data/p_taucov/linear/source/G_Phi.csv
data/p_taucov/linear/source/G_B.csv
data/p_taucov/linear/source/P0_source.csv
evidence/p_taucov_linear_source_manifest.yaml
evidence/p_taucov_linear_source.sha256
evidence/p_taucov_linear_source_leakage_audit.csv
```

## Acceptance Conditions

The source packet may be accepted only if:

```text
all required source files exist;
dimensions are compatible with the frozen coordinate basis and P_red domain;
source origins are target-blind and match the Tau-side definitions;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
hash file matches every source object;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The finite-dimensional linear-source packet gate is declared.
```

Forbidden statement:

```text
The finite-dimensional source objects or derived linear matrices are frozen.
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
