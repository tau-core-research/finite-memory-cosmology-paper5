#!/usr/bin/env python3
"""Build the P-TauCov coordinate-basis packet gate document."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_coordinate_basis_packet_gate.md"
OUT_CSV = EVIDENCE / "p_taucov_coordinate_basis_packet_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_coordinate_basis_packet_gate_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_COORDINATE_BASIS_PACKET_GATE_v1"
CLAIM_BOUNDARY = "coordinate_basis_packet_gate_declared_packet_not_supplied"

REQUIRED_FILES = [
    {
        "Path": "data/p_taucov/linear/coordinate_basis.csv",
        "Role": "concrete coordinate/source basis rows",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_coordinate_basis_manifest.yaml",
        "Role": "packet provenance, source policy, freeze timestamp, and no-outcome declaration",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_coordinate_basis.sha256",
        "Role": "sha256 digest of coordinate_basis.csv",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_coordinate_basis_leakage_audit.csv",
        "Role": "row-level or source-level leakage audit proving no target/residual/score-derived basis fields",
        "Required": True,
    },
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
                "ConcretePacketSupplied": False,
                "ReferenceDomainSelectable": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row in REQUIRED_FILES
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "GateID": GATE_ID,
                "RequiredFiles": len(df),
                "PacketGateDeclared": True,
                "ConcretePacketSupplied": False,
                "CoordinateBasisFrozen": False,
                "ReferenceDomainSelectable": False,
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_coordinate_basis_packet_then_run_packet_validator",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Coordinate-Basis Packet Gate

Status: packet gate / no concrete coordinate basis / no reference-domain
selection / no linear packet / no metric evaluation / no scoring authorization.

This artifact defines the acceptance gate for the concrete coordinate/source
basis packet required by the P-TauCov reference-domain selection rule.

## Required Files

| File | Purpose |
| --- | --- |
| `data/p_taucov/linear/coordinate_basis.csv` | Concrete coordinate/source basis rows. |
| `evidence/p_taucov_coordinate_basis_manifest.yaml` | Provenance, source policy, freeze timestamp, and no-outcome declaration. |
| `evidence/p_taucov_coordinate_basis.sha256` | SHA256 digest of `coordinate_basis.csv`. |
| `evidence/p_taucov_coordinate_basis_leakage_audit.csv` | Leakage audit proving no target/residual/score-derived basis fields. |

## Packet Acceptance Checks

The packet validator must reject the packet unless:

```text
all required files exist;
all schema fields are present in coordinate_basis.csv;
coordinate_id values are unique;
origin_value values are finite;
scale_value values are finite and nonzero;
provenance is nonempty for every row;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
sha256 file matches coordinate_basis.csv;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The coordinate-basis packet acceptance gate is declared.
```

Forbidden statement:

```text
The concrete coordinate-basis packet has been accepted or frozen.
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
