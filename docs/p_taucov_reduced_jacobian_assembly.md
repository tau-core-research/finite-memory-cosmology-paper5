# P-TauCov Reduced-Jacobian Assembly

Freeze ID: `P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLY_v1`

Status:

`P_TAUCOV_REDUCED_JACOBIAN_ASSEMBLED_NO_SCORING`

## Purpose

This artifact assembles the first conservative reduced-Jacobian source object
from previously validated, target-blind source artifacts. It does not authorize
empirical scoring and does not claim Tau Core validation.

## Assembly Rule

The v1 assembly uses the strict branch-only rule:

```text
J_response = P_red D_B M_proj P_red * (delta B / delta Phi)
```

with:

```text
delta B / delta Phi = -0.4999999999999999
```

The projection-coordinate derivative is not included in this v1 assembly,
because `D_P M_proj` has not been separately frozen.

The full-action reduced projector is applied before writing the assembly
matrix, so gauge and forbidden coordinates are excluded from this v1 object.

## Covariance Candidate

The associated no-scoring covariance candidate is the target-blind PSD lift:

```text
delta_C_Tau = J_response J_response^T / ||J_response J_response^T||_F
```

## Key Numbers

- `||J_response||_F = 0.7071067811865474`
- `||delta_C_Tau||_F = 0.9999999999999999`
- `min eig(delta_C_Tau) = 0.0`
- `max eig(delta_C_Tau) = 0.7071067811865475`
- forbidden/gauge leakage norm: `0.0`
- gates passed: `8/8`

## Claim Boundary

Allowed statement:

> A conservative strict-branch reduced-Jacobian source object has been
> assembled without target or score inputs.

Forbidden statement:

> This artifact authorizes scoring, establishes survival, or validates Tau
> Core.
