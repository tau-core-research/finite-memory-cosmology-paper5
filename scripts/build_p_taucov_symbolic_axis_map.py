#!/usr/bin/env python3
"""Build the P-TauCov finite-dimensional symbolic axis map."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_symbolic_axis_map.md"
OUT_CSV = EVIDENCE / "p_taucov_symbolic_axis_map.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_symbolic_axis_map_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
MAP_ID = "P_TAUCOV_SYMBOLIC_AXIS_MAP_v1"
CLAIM_BOUNDARY = "symbolic_axis_map_declared_no_numeric_basis_no_matrices"

ROWS = [
    {
        "AxisID": "PHI_PARENT_SOURCE",
        "AxisFamily": "Phi",
        "AxisKind": "parent",
        "SymbolicRole": "parent perturbation coordinate delta Phi",
        "AllowedSourceClass": "TauSideSymbolicDefinition",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "B_BRANCH_RESPONSE",
        "AxisFamily": "B",
        "AxisKind": "branch",
        "SymbolicRole": "relaxed branch response coordinate B_*(Phi)",
        "AllowedSourceClass": "TauSideSymbolicDefinition",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "M_PARENT_MORPHOLOGY",
        "AxisFamily": "M",
        "AxisKind": "morphology",
        "SymbolicRole": "parent morphology carrier M_parent(Phi,B)",
        "AllowedSourceClass": "TauSideSymbolicDefinition",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "P_MORPH_PROJECTION",
        "AxisFamily": "P",
        "AxisKind": "projection",
        "SymbolicRole": "fixed morphology projection map P_morph",
        "AllowedSourceClass": "TauSideSymbolicDefinition",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "COORD_ORIGIN_CENTER",
        "AxisFamily": "CoordinateConvention",
        "AxisKind": "reference",
        "SymbolicRole": "origin or center convention for Phi_0 selection",
        "AllowedSourceClass": "CoordinateConventionOnly",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "COORD_SCALE_UNIT",
        "AxisFamily": "CoordinateConvention",
        "AxisKind": "scale",
        "SymbolicRole": "target-blind unit or normalization convention",
        "AllowedSourceClass": "CoordinateConventionOnly",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "EXT_SOURCE_FAMILY",
        "AxisFamily": "ExternalMetadata",
        "AxisKind": "family",
        "SymbolicRole": "citable external source-family or observing-context tag",
        "AllowedSourceClass": "PublishedExternalMetadata",
        "MayEnterCoordinateBasis": True,
    },
    {
        "AxisID": "EXT_OBSERVING_CONTEXT",
        "AxisFamily": "ExternalMetadata",
        "AxisKind": "context",
        "SymbolicRole": "citable target-blind observing-context descriptor",
        "AllowedSourceClass": "PublishedExternalMetadata",
        "MayEnterCoordinateBasis": True,
    },
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "MapID": MAP_ID,
                **row,
                "NumericValueSupplied": False,
                "MatrixElementSupplied": False,
                "UsesResidualOrScore": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
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
                "MapID": MAP_ID,
                "SymbolicAxesDeclared": len(df),
                "NumericValuesSupplied": 0,
                "MatrixElementsSupplied": 0,
                "ResidualOrScoreUse": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "derive_coordinate_basis_rows_from_symbolic_axis_map",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Finite-Dimensional Symbolic Axis Map

Status: symbolic axis map / no numeric basis rows / no matrices / no reference
domain / no metric evaluation / no scoring authorization.

This artifact converts the allowed source classes into a finite-dimensional
symbolic axis map. It declares the kinds of axes a later coordinate-basis packet
may instantiate, but it does not yet provide numerical `origin_value`,
`scale_value`, matrix elements, or a concrete `Phi_0`.

## Symbolic Axes

| Axis | Role | Allowed source class |
| --- | --- | --- |
| `PHI_PARENT_SOURCE` | Parent perturbation coordinate `delta Phi`. | Tau-side symbolic definition |
| `B_BRANCH_RESPONSE` | Relaxed branch response coordinate `B_*(Phi)`. | Tau-side symbolic definition |
| `M_PARENT_MORPHOLOGY` | Parent morphology carrier `M_parent(Phi,B)`. | Tau-side symbolic definition |
| `P_MORPH_PROJECTION` | Fixed morphology projection map `P_morph`. | Tau-side symbolic definition |
| `COORD_ORIGIN_CENTER` | Origin or center convention for `Phi_0` selection. | Coordinate convention only |
| `COORD_SCALE_UNIT` | Target-blind unit or normalization convention. | Coordinate convention only |
| `EXT_SOURCE_FAMILY` | Citable external source-family or observing-context tag. | Published external metadata |
| `EXT_OBSERVING_CONTEXT` | Citable target-blind observing-context descriptor. | Published external metadata |

## Guardrails

This map must not use:

```text
P5C v3 gains;
held-out residuals;
OOS DeltaNLL;
post-hoc family localization;
metric pass/fail outcomes.
```

## What This Enables

The next artifact may derive concrete `coordinate_basis.csv` rows from this map.
That future packet still requires provenance, hashes, a leakage audit, finite
origin and scale values, and manifest flags declaring no outcome, residual,
score, or post-scoring localization use.

## Claim Boundary

Allowed statement:

```text
A finite-dimensional symbolic axis map is declared.
```

Forbidden statement:

```text
The concrete coordinate basis, matrices, or P-TauCov covariance response are
available.
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
