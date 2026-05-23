#!/usr/bin/env python3
"""Build the P-TauCov origin/scale rule freeze."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_origin_scale_rule_freeze.md"
OUT_CSV = EVIDENCE / "p_taucov_origin_scale_rule_freeze.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_origin_scale_rule_freeze_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_ORIGIN_SCALE_RULE_FREEZE_v1"
CLAIM_BOUNDARY = "origin_scale_rules_frozen_no_values_no_packet"

ROWS = [
    {
        "AxisKind": "parent",
        "OriginRule": "theory_declared_zero",
        "ScaleRule": "theory_declared_unit_or_predeclared_finite_unit",
        "AllowedInput": "Tau_side_symbolic_definition",
    },
    {
        "AxisKind": "branch",
        "OriginRule": "stationary_branch_reference_zero_before_solving_B_star",
        "ScaleRule": "theory_declared_branch_unit_or_predeclared_finite_unit",
        "AllowedInput": "Tau_side_symbolic_definition",
    },
    {
        "AxisKind": "morphology",
        "OriginRule": "predeclared_morphology_baseline_zero_or_center",
        "ScaleRule": "predeclared_morphology_unit",
        "AllowedInput": "Tau_side_symbolic_definition_or_external_metadata_units",
    },
    {
        "AxisKind": "projection",
        "OriginRule": "identity_projection_reference",
        "ScaleRule": "unit_projection_norm",
        "AllowedInput": "Tau_side_symbolic_definition",
    },
    {
        "AxisKind": "reference",
        "OriginRule": "coordinate_basis_origin_if_declared_else_coordinate_center",
        "ScaleRule": "unit_reference_scale",
        "AllowedInput": "coordinate_convention_only",
    },
    {
        "AxisKind": "scale",
        "OriginRule": "zero_log_or_additive_scale_reference",
        "ScaleRule": "declared_unit_scale",
        "AllowedInput": "coordinate_convention_only",
    },
    {
        "AxisKind": "family",
        "OriginRule": "categorical_reference_baseline_declared_before_scoring",
        "ScaleRule": "unit_indicator_scale",
        "AllowedInput": "published_external_metadata",
    },
    {
        "AxisKind": "context",
        "OriginRule": "external_context_baseline_declared_before_scoring",
        "ScaleRule": "published_unit_or_unit_indicator_scale",
        "AllowedInput": "published_external_metadata",
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
                "ConcreteOriginValueSupplied": False,
                "ConcreteScaleValueSupplied": False,
                "UsesOutcomeInformation": False,
                "UsesResidualInformation": False,
                "UsesScoreInformation": False,
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
                "FreezeID": FREEZE_ID,
                "AxisKindsCovered": len(df),
                "RulesFrozen": True,
                "ConcreteOriginValuesSupplied": 0,
                "ConcreteScaleValuesSupplied": 0,
                "OutcomeResidualScoreUse": False,
                "CoordinateBasisPacketAuthorized": False,
                "ReferenceDomainSelectable": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "apply_origin_scale_rules_to_skeleton_with_real_target_blind_values",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Origin/Scale Rule Freeze

Status: origin/scale rule freeze / no concrete origin values / no concrete
scale values / no coordinate-basis packet / no metric evaluation / no scoring
authorization.

This artifact freezes how future coordinate-basis rows may receive
`origin_value` and `scale_value`. It does not fill the values. The purpose is to
prevent post-hoc normalization choices after residual or score inspection.

## Frozen Rules By Axis Kind

| Axis kind | Origin rule | Scale rule |
| --- | --- | --- |
| `parent` | theory-declared zero | theory-declared unit or predeclared finite unit |
| `branch` | stationary branch reference zero before solving `B_*` | theory-declared branch unit or predeclared finite unit |
| `morphology` | predeclared morphology baseline zero or center | predeclared morphology unit |
| `projection` | identity-projection reference | unit projection norm |
| `reference` | coordinate-basis origin if declared, otherwise coordinate center | unit reference scale |
| `scale` | zero log/additive scale reference | declared unit scale |
| `family` | categorical reference baseline declared before scoring | unit indicator scale |
| `context` | external context baseline declared before scoring | published unit or unit indicator scale |

## Forbidden Inputs

The origin and scale rules must not use:

```text
held-out residuals;
P5C v3 gains;
OOS DeltaNLL;
family-localized covariance score;
linear specificity pass/fail;
post-hoc support localization.
```

## Claim Boundary

Allowed statement:

```text
The origin/scale selection rules are frozen.
```

Forbidden statement:

```text
Concrete origin/scale values or a coordinate-basis packet are frozen.
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
