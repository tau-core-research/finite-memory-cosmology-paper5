# P-TauCov Linear Specificity Metric Registry

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
