#!/usr/bin/env python3
"""Build the P-TauCov origin/scale value-source packet gate."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_origin_scale_value_source_gate.md"
OUT_CSV = EVIDENCE / "p_taucov_origin_scale_value_source_gate.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_origin_scale_value_source_gate_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
GATE_ID = "P_TAUCOV_ORIGIN_SCALE_VALUE_SOURCE_GATE_v1"
CLAIM_BOUNDARY = "origin_scale_value_source_gate_declared_values_not_supplied"

REQUIRED_FILES = [
    {
        "Path": "data/p_taucov/linear/origin_scale_values.csv",
        "Role": "target-blind concrete origin and scale values keyed by basis_axis",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_origin_scale_values_manifest.yaml",
        "Role": "provenance, rule conformance, and no-outcome declaration for origin/scale values",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_origin_scale_values.sha256",
        "Role": "sha256 digest of origin_scale_values.csv",
        "Required": True,
    },
    {
        "Path": "evidence/p_taucov_origin_scale_values_leakage_audit.csv",
        "Role": "leakage audit proving no residual, score, or post-scoring source was used",
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
                "ConcreteValuesSupplied": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
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
                "ValueSourceGateDeclared": True,
                "ConcreteValuesSupplied": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_origin_scale_value_sources_then_validate",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Origin/Scale Value-Source Gate

Status: value-source gate / no concrete origin values / no concrete scale
values / no coordinate-basis packet / no metric evaluation / no scoring
authorization.

The origin/scale rule freeze states how values may be selected. This artifact
defines the packet required before those placeholders can be filled in the
coordinate-basis skeleton.

## Required Files

| File | Purpose |
| --- | --- |
| `data/p_taucov/linear/origin_scale_values.csv` | Target-blind concrete `origin_value` and `scale_value` rows keyed by `basis_axis`. |
| `evidence/p_taucov_origin_scale_values_manifest.yaml` | Provenance, rule conformance, and no-outcome declaration. |
| `evidence/p_taucov_origin_scale_values.sha256` | SHA256 digest of `origin_scale_values.csv`. |
| `evidence/p_taucov_origin_scale_values_leakage_audit.csv` | Leakage audit proving no residual, score, or post-scoring source was used. |

## Expected CSV Columns

```text
basis_axis
origin_value
scale_value
origin_rule
scale_rule
value_source
provenance
```

## Hard Acceptance Conditions

The value-source packet may be accepted only if:

```text
all required files exist;
all expected columns are present;
all basis_axis values are unique;
origin_value and scale_value are finite;
scale_value is nonzero;
origin_rule and scale_rule match the frozen axis-kind rules;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
sha256 file matches origin_scale_values.csv;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The origin/scale value-source acceptance gate is declared.
```

Forbidden statement:

```text
Concrete origin/scale values or a coordinate-basis packet are available.
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
