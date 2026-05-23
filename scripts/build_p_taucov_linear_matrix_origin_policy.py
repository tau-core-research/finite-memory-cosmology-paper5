#!/usr/bin/env python3
"""Build the P-TauCov linear matrix-origin policy."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_matrix_origin_policy.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_matrix_origin_policy.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_matrix_origin_policy_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
POLICY_ID = "P_TAUCOV_LINEAR_MATRIX_ORIGIN_POLICY_v1"
CLAIM_BOUNDARY = "matrix_origin_policy_no_packet_no_metric_evaluation"

ROWS = [
    ("L0_B", "TAU_OPERATOR_REQUIRED", "must come from declared branch relaxation geometry/operator, not identity-by-default"),
    ("R_B", "TAU_COUPLING_REQUIRED", "must come from declared parent-to-branch forcing rule"),
    ("P_red", "DOMAIN_POLICY_REQUIRED", "must encode invertible branch domain and null/gauge exclusions"),
    ("A_Phi", "MORPHOLOGY_MAP_REQUIRED", "must come from parent morphology definition, not outcome correlation"),
    ("A_B", "MORPHOLOGY_MAP_REQUIRED", "must come from branch contribution to morphology"),
    ("P0", "PROJECTION_RULE_REQUIRED", "must come from declared projection map or observational coordinate projection"),
    ("coordinate_basis", "POLICY_FREEZABLE", "may reuse frozen source coordinate basis if declared before metric evaluation"),
]

FORBIDDEN = [
    "choosing matrices to increase prescore metric pass count",
    "using held-out residuals",
    "using P5C v3 family gain localization",
    "using OOS DeltaNLL or failed v3 gates",
    "using signed diagnostic advantage",
    "post-hoc rank or entropy tuning",
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PolicyID": POLICY_ID,
                "ObjectID": obj,
                "OriginClass": origin,
                "OriginRequirement": requirement,
                "ConcreteSourcePresent": False,
                "MayUseGenericDefault": False if obj != "coordinate_basis" else True,
                "RequiredBeforePacket": True,
                "MetricEvaluationAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for obj, origin, requirement in ROWS
        ]
    )
    df.to_csv(OUT_CSV, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PolicyID": POLICY_ID,
                "ObjectsCovered": len(df),
                "ConcreteSourcesPresent": int(df["ConcreteSourcePresent"].astype(bool).sum()),
                "GenericDefaultsAllowed": int(df["MayUseGenericDefault"].astype(bool).sum()),
                "ForbiddenInputs": ";".join(FORBIDDEN),
                "LinearPacketAuthorized": False,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "NextStep": "supply_theory_origin_for_L0_B_R_B_A_Phi_A_B_P0",
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear Matrix-Origin Policy

Status: origin policy / no packet / no metric evaluation / no scoring
authorization.

This policy prevents the linear model packet from becoming an arbitrary matrix
exercise. Each matrix must have a target-blind origin before it can enter
`evidence/p_taucov_linear_model_packet.yaml`.

## Required Origins

| Object | Required origin |
| --- | --- |
| `L0_B` | Tau-side branch relaxation geometry/operator. |
| `R_B` | Parent-to-branch forcing rule. |
| `P_red` | Invertible branch-domain policy with null/gauge exclusions. |
| `A_Phi` | Parent morphology definition. |
| `A_B` | Branch contribution to morphology. |
| `P0` | Declared projection map or observational coordinate projection. |
| `coordinate_basis` | Frozen source coordinate basis, if declared before evaluation. |

## Forbidden Origins

```text
choosing matrices to increase prescore metric pass count;
using held-out residuals;
using P5C v3 family gain localization;
using OOS DeltaNLL or failed v3 gates;
using signed diagnostic advantage;
post-hoc rank or entropy tuning.
```

## Important Boundary

Generic defaults such as identity, diagonal smoothing, or random low-rank
matrices are allowed only as null comparators. They are not allowed as the Tau
candidate origin for `L0_B`, `R_B`, `A_Phi`, `A_B`, or `P0`.

Allowed statement:

```text
The matrix-origin policy defines what a valid target-blind linear packet must
justify.
```

Forbidden statement:

```text
The required linear packet matrices have already been derived.
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
