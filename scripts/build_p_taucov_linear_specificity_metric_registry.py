#!/usr/bin/env python3
"""Build the P-TauCov linear specificity prescore metric registry."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

OUT_DOC = DOCS / "p_taucov_linear_specificity_metric_registry.md"
OUT_CSV = EVIDENCE / "p_taucov_linear_specificity_metric_registry.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_linear_specificity_metric_registry_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
AUDIT_ID = "P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1"
REGISTRY_ID = "P_TAUCOV_LINEAR_SPECIFICITY_METRIC_REGISTRY_v1"
CLAIM_BOUNDARY = "linear_specificity_metric_registry_prescore_only_no_freeze"


ROWS = [
    {
        "MetricID": "M1_NONCOMMUTATOR_SHARE",
        "Gate": "LSA3",
        "Definition": "norm([P_morph,L_B_red_inverse_R_B]) / norm(P_morph L_B_red_inverse_R_B)",
        "PassDirection": "higher",
        "MinimumRequirement": "must exceed frozen epsilon_comm threshold",
    },
    {
        "MetricID": "M2_EFFECTIVE_RANK",
        "Gate": "LSA2",
        "Definition": "effective_rank(delta_C_Tau_linear_candidate)",
        "PassDirection": "not_too_low_not_full_generic",
        "MinimumRequirement": "must not collapse to rank1_or_diagonal_template",
    },
    {
        "MetricID": "M3_SUPPORT_ENTROPY",
        "Gate": "LSA4",
        "Definition": "entropy(W_branch_from_linear_delta_C_Tau)",
        "PassDirection": "bounded",
        "MinimumRequirement": "must be neither single_family_proxy nor uniform_noise",
    },
    {
        "MetricID": "M4_LABEL_PROXY_OVERLAP",
        "Gate": "LSA4",
        "Definition": "overlap(predicted_support, known_family_or_clock_blocks)",
        "PassDirection": "lower",
        "MinimumRequirement": "must stay below frozen label_proxy_threshold",
    },
    {
        "MetricID": "M5_NULL_SEPARATION_MARGIN",
        "Gate": "LSA5",
        "Definition": "structural_distance(candidate, strongest_prescore_linear_null)",
        "PassDirection": "higher",
        "MinimumRequirement": "must be positive against all declared prescore nulls",
    },
    {
        "MetricID": "M6_OUTCOME_LEAKAGE_CERTIFICATE",
        "Gate": "LSA1",
        "Definition": "input provenance hash audit for absence of held_out_residuals and P5C_v3 outcome fields",
        "PassDirection": "boolean_true",
        "MinimumRequirement": "must pass before any metric is interpreted",
    },
]

NULLS = [
    "SHUFFLED_BRANCH_OPERATOR",
    "COMMUTING_PROJECTION_NULL",
    "RANDOM_LOW_RANK_LINEAR_NULL",
    "DIAGONAL_LINEAR_NULL",
    "FAMILY_LABEL_PROXY_NULL",
    "CLOCK_BLOCK_PROXY_NULL",
]


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "AuditID": AUDIT_ID,
                "RegistryID": REGISTRY_ID,
                **row,
                "RequiredBeforeLinearFreeze": True,
                "UsesTargetResiduals": False,
                "UsesP5Cv3Outcome": False,
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
                "AuditID": AUDIT_ID,
                "RegistryID": REGISTRY_ID,
                "MetricsDeclared": len(df),
                "PrescoreNullsDeclared": len(NULLS),
                "LinearCandidateFrozen": False,
                "DeltaCTauGenerated": False,
                "PTauCovScoringAuthorized": False,
                "PrescoreNulls": ";".join(NULLS),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        """# P-TauCov Linear Specificity Metric Registry

Status: prescore metric registry / no linear freeze / no `delta_C_Tau` scoring.

This registry defines the target-blind structural metrics required by
`P_TAUCOV_LINEAR_SPECIFICITY_AUDIT_v1`. The metrics are evaluated before any
P-TauCov alignment score. They decide whether the strictly linear candidate is
specific enough to freeze, or too generic.

## Metrics

| Metric | Purpose |
| --- | --- |
| `M1_NONCOMMUTATOR_SHARE` | Tests whether branch relaxation and projection fail to commute trivially. |
| `M2_EFFECTIVE_RANK` | Blocks collapse into rank-1 or diagonal covariance templates. |
| `M3_SUPPORT_ENTROPY` | Blocks both single-family proxy and uniform-noise support. |
| `M4_LABEL_PROXY_OVERLAP` | Quantifies overlap with known family/clock labels before scoring. |
| `M5_NULL_SEPARATION_MARGIN` | Requires separation from strongest declared prescore linear null. |
| `M6_OUTCOME_LEAKAGE_CERTIFICATE` | Confirms no held-out residual or P5C v3 outcome field enters. |

## Declared Prescore Nulls

```text
SHUFFLED_BRANCH_OPERATOR
COMMUTING_PROJECTION_NULL
RANDOM_LOW_RANK_LINEAR_NULL
DIAGONAL_LINEAR_NULL
FAMILY_LABEL_PROXY_NULL
CLOCK_BLOCK_PROXY_NULL
```

## Decision Boundary

The strictly linear candidate may only advance to a concrete freeze if all
registered metrics pass under thresholds frozen before evaluation. Passing this
registry does not authorize P-TauCov scoring; it only authorizes the next
manifest step.

Forbidden statement:

```text
The linear metric registry proves a Tau covariance signal.
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
