#!/usr/bin/env python3
"""Build the P-TauCov linear-object derivation gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_object_derivation_gate.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_object_derivation_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_object_derivation_gate_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_LINEAR_OBJECT_DERIVATION_GATE_v1"
CLAIM_BOUNDARY = "linear_object_derivation_gate_declared_no_matrices"

ROWS = [
    {
        "Object": "L0_B",
        "RequiredOrigin": "P_red D_B F_B|(Phi_0,B_*) P_red",
        "RequiredSourcePacket": "finite_dimensional_K_B_Gamma_B_packet",
        "ExpectedFile": "data/p_taucov/linear/L0_B.csv",
    },
    {
        "Object": "R_B",
        "RequiredOrigin": "- P_red D_Phi F_B|(Phi_0,B_*)",
        "RequiredSourcePacket": "finite_dimensional_DPhi_K_B_DPhi_J_B_packet",
        "ExpectedFile": "data/p_taucov/linear/R_B.csv",
    },
    {
        "Object": "A_Phi",
        "RequiredOrigin": "D_Phi M_parent|(Phi_0,B_*)",
        "RequiredSourcePacket": "target_blind_G_Phi_packet",
        "ExpectedFile": "data/p_taucov/linear/A_Phi.csv",
    },
    {
        "Object": "A_B",
        "RequiredOrigin": "D_B M_parent|(Phi_0,B_*)",
        "RequiredSourcePacket": "target_blind_G_B_packet",
        "ExpectedFile": "data/p_taucov/linear/A_B.csv",
    },
    {
        "Object": "P0",
        "RequiredOrigin": "P_morph(Phi_0,B_*(Phi_0)) or declared coordinate projection",
        "RequiredSourcePacket": "fixed_morphology_projection_packet",
        "ExpectedFile": "data/p_taucov/linear/P0.csv",
    },
]

REQUIRED_PACKET_FILES = [
    "data/p_taucov/linear/L0_B.csv",
    "data/p_taucov/linear/R_B.csv",
    "data/p_taucov/linear/A_Phi.csv",
    "data/p_taucov/linear/A_B.csv",
    "data/p_taucov/linear/P0.csv",
    "evidence/p_taucov_linear_object_derivation_manifest.yaml",
    "evidence/p_taucov_linear_object_derivation.sha256",
    "evidence/p_taucov_linear_object_derivation_leakage_audit.csv",
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
                "ConcreteObjectSupplied": False,
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
                "ObjectsDeclared": len(df),
                "RequiredPacketFiles": len(REQUIRED_PACKET_FILES),
                "LinearObjectGateDeclared": True,
                "ConcreteObjectsSupplied": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_target_blind_finite_dimensional_linear_objects",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear-Object Derivation Gate

Status: derivation gate / no concrete linear matrices / no covariance response
/ no metric evaluation / no scoring authorization.

The reference-domain packet freezes `Phi_0` and `P_red`. This gate defines what
must be supplied before the Tau-side linear objects can be accepted.

## Required Linear Objects

| Object | Required origin | Expected file |
| --- | --- | --- |
| `L0_B` | `P_red D_B F_B|(Phi_0,B_*) P_red` | `data/p_taucov/linear/L0_B.csv` |
| `R_B` | `- P_red D_Phi F_B|(Phi_0,B_*)` | `data/p_taucov/linear/R_B.csv` |
| `A_Phi` | `D_Phi M_parent|(Phi_0,B_*)` | `data/p_taucov/linear/A_Phi.csv` |
| `A_B` | `D_B M_parent|(Phi_0,B_*)` | `data/p_taucov/linear/A_B.csv` |
| `P0` | `P_morph(Phi_0,B_*(Phi_0))` or declared coordinate projection | `data/p_taucov/linear/P0.csv` |

## Required Packet Files

```text
data/p_taucov/linear/L0_B.csv
data/p_taucov/linear/R_B.csv
data/p_taucov/linear/A_Phi.csv
data/p_taucov/linear/A_B.csv
data/p_taucov/linear/P0.csv
evidence/p_taucov_linear_object_derivation_manifest.yaml
evidence/p_taucov_linear_object_derivation.sha256
evidence/p_taucov_linear_object_derivation_leakage_audit.csv
```

## Acceptance Conditions

The packet may be accepted only if:

```text
all required objects exist;
matrix dimensions match the frozen coordinate basis and P_red domain;
object origins match the declared Tau-side routes;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
hash file matches every matrix;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The linear-object derivation gate is declared.
```

Forbidden statement:

```text
The Tau-side linear matrices or covariance response are frozen.
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
