# P-TauCov Projected Morphology Derivative Audit

Freeze ID: `P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_AUDIT_v1`

Status:

`P_TAUCOV_PROJECTED_MORPHOLOGY_DERIVATIVE_PASS_NO_SCORING`

## Purpose

This audit resolves whether the strict-linear P-TauCov source packet already
provides the projected morphology derivatives required by the reduced
branch-Jacobian route.

It does not authorize scoring and does not claim a physical morphology model.

## Strict-Linear Rule

With fixed projection `P0` and linear parent morphology maps:

```text
M_parent(Phi,B) = A_Phi Phi + A_B B
```

the projected morphology derivatives are:

```text
D_B M_proj = P0 A_B
D_Phi M_proj = P0 A_Phi
```

The derivative of `P_morph` itself is intentionally excluded in this strict
linear pass:

```text
D_B P_morph = 0
```

## Key Numbers

- `||D_B M_proj||_F = 2.23606797749979`
- `||D_Phi M_proj||_F = 2.23606797749979`
- gates passed: `7/7`

## Claim Boundary

Allowed statement:

> A strict-linear, target-blind projected morphology derivative has been
> computed from frozen `P0`, `A_B`, and `A_Phi`.

Forbidden statement:

> This derivative is a physical morphology model, authorizes scoring, or
> validates Tau Core.
