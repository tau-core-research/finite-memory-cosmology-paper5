# P-TauCov Projection-Coupled Jacobian Assembly

Freeze ID: `P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLY_v1`

Status:

`P_TAUCOV_PROJECTION_COUPLED_JACOBIAN_ASSEMBLED_NO_SCORING`

## Purpose

This artifact assembles the first projection-coupled reduced-Jacobian source
object. It is a no-scoring assembly step, not an empirical result.

## Assembly Rule

```text
J_response =
  P_red [ D_B M_proj (delta B / delta Phi)
        + D_P M_proj (delta P / delta Phi) ] P_red
```

with:

```text
delta B / delta Phi = -0.4999999999999999
delta P / delta Phi = 0.2499999999999999
```

The `D_P M_proj` source is frozen separately in:

[`p_taucov_d_p_mproj_source_spec.md`](p_taucov_d_p_mproj_source_spec.md)

## Key Numbers

- `||J_response||_F = 0.7499999999999998`
- `||delta_C_Tau||_F = 1.0`
- diagonal energy share: `0.9493337494797257`
- active projection commutator share: `0.3142696805273544`
- forbidden/gauge leakage norm: `0.0`
- gates passed: `9/9`

## Claim Boundary

Allowed statement:

> A target-blind projection-coupled reduced-Jacobian source object has been
> assembled for preflight testing.

Forbidden statement:

> This artifact authorizes scoring, establishes survival, or validates Tau
> Core.
