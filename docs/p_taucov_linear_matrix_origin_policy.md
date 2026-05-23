# P-TauCov Linear Matrix-Origin Policy

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
