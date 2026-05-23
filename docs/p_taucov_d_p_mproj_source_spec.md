# P-TauCov D_P M_proj Source Spec

Freeze ID: `P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_v1`

Status:

`P_TAUCOV_D_P_MPROJ_SOURCE_SPEC_FROZEN_NO_OBJECT_NO_SCORING`

## Purpose

The strict branch-only reduced-Jacobian candidate failed because it had no
explicit projection/morphology channel. This source spec freezes the minimal
target-blind projection derivative needed for the next assembly attempt.

It is not a new `delta_C_Tau` candidate and does not authorize scoring.

## Source Rule

The frozen derivative source is the minimal symmetric active coupling between
the branch response coordinate and the projected morphology coordinate:

```text
D_P M_proj(B, P) =
  ( |B><P| + |P><B| ) / sqrt(2)
```

where:

```text
B = TEMPLATE_B_BRANCH_RESPONSE
P = TEMPLATE_P_MORPH_PROJECTION
```

Direct `TEMPLATE_M_PARENT_MORPHOLOGY` support remains forbidden in the reduced
object. The parent morphology axis may motivate the route, but it is not
allowed to leak into the scoreable reduced coordinate object.

## Key Diagnostics

- Frobenius norm: `0.9999999999999999`
- diagonal energy share: `0.0`
- active `P_morph` commutator share: `1.0`
- reduced-domain norm: `0.9999999999999999`
- forbidden/gauge leakage norm: `0.0`
- gates passed: `9/9`

## Claim Boundary

Allowed statement:

> A target-blind `D_P M_proj` source derivative has been frozen for the next
> P-TauCov assembly attempt.

Forbidden statement:

> This derivative constructs a new covariance candidate, authorizes scoring,
> survives a Tau-specific test, or validates Tau Core.
