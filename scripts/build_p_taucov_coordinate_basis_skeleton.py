#!/usr/bin/env python3
"""Build a non-authorizing P-TauCov coordinate-basis skeleton."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
TEMPLATES = ROOT / "data/p_taucov/templates"

AXIS_MAP = EVIDENCE / "p_taucov_symbolic_axis_map.csv"
OUT_DOC = DOCS / "p_taucov_coordinate_basis_skeleton.md"
OUT_TEMPLATE = TEMPLATES / "coordinate_basis_skeleton.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_coordinate_basis_skeleton_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
SKELETON_ID = "P_TAUCOV_COORDINATE_BASIS_SKELETON_v1"
CLAIM_BOUNDARY = "coordinate_basis_skeleton_template_no_packet_no_freeze"


def build_rows(axis_map: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for _, axis in axis_map.iterrows():
        axis_id = axis["AxisID"]
        axis_kind = axis["AxisKind"]
        axis_family = axis["AxisFamily"]
        rows.append(
            {
                "coordinate_id": f"TEMPLATE_{axis_id}",
                "coordinate_family": axis_family,
                "coordinate_kind": axis_kind,
                "basis_axis": axis_id,
                "origin_value": "TO_BE_FILLED_BY_TARGET_BLIND_PACKET",
                "scale_value": "TO_BE_FILLED_BY_TARGET_BLIND_PACKET",
                "is_null_candidate": False,
                "is_gauge_candidate": axis_kind in {"projection", "reference", "scale"},
                "is_forbidden_candidate": False,
                "provenance": f"derived_from_{axis['AllowedSourceClass']}_via_{axis_id}",
                "TemplateOnly": True,
                "NumericValueSupplied": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    TEMPLATES.mkdir(parents=True, exist_ok=True)

    if not AXIS_MAP.exists():
        raise FileNotFoundError(f"Missing symbolic axis map: {AXIS_MAP}")

    axis_map = pd.read_csv(AXIS_MAP)
    template = pd.DataFrame(build_rows(axis_map))
    template.to_csv(OUT_TEMPLATE, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "SkeletonID": SKELETON_ID,
                "TemplateRows": len(template),
                "TemplateOnly": True,
                "NumericValuesSupplied": 0,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "TemplatePath": str(OUT_TEMPLATE.relative_to(ROOT)),
                "NextStep": "replace_template_placeholders_with_target_blind_packet_values_and_manifest",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Coordinate-Basis Skeleton

Status: template only / no concrete coordinate-basis packet / no frozen
`Phi_0` / no reduced domain / no metric evaluation / no scoring authorization.

This artifact derives a non-authorizing coordinate-basis skeleton from the
finite-dimensional symbolic axis map. The file is intentionally stored under
`data/p_taucov/templates/`, not at the packet path
`data/p_taucov/linear/coordinate_basis.csv`.

## Template File

```text
data/p_taucov/templates/coordinate_basis_skeleton.csv
```

The template uses the schema columns expected by the future packet, but the
numeric fields are placeholders:

```text
origin_value = TO_BE_FILLED_BY_TARGET_BLIND_PACKET
scale_value  = TO_BE_FILLED_BY_TARGET_BLIND_PACKET
```

Therefore this skeleton must not be accepted by the coordinate-basis packet
validator.

## Guardrail

The skeleton is useful only as a derivation aid. It does not authorize:

```text
coordinate-basis packet acceptance;
reference-domain selection;
matrix construction;
linear specificity metric evaluation;
P-TauCov scoring.
```

## Claim Boundary

Allowed statement:

```text
A coordinate-basis skeleton template has been derived from the symbolic axis map.
```

Forbidden statement:

```text
The concrete coordinate basis has been supplied, accepted, or frozen.
```
""",
        encoding="utf-8",
    )

    print(f"Wrote {OUT_DOC}")
    print(f"Wrote {OUT_TEMPLATE}")
    print(f"Wrote {OUT_SUMMARY}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
