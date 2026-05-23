# P-TauCov Branch-Equation Completion Audit

Freeze ID: `P_TAUCOV_BRANCH_EQUATION_COMPLETION_AUDIT_v1`

Status:

`P_TAUCOV_BRANCH_EQUATION_PARTIAL_COMPLETION_MEDIATED_FORCING_REQUIRED_NO_SCORING`

## Purpose

This audit asks whether the existing target-blind action scaffold already
completes the branch equation needed for the reduced branch-Jacobian route.
It does not authorize scoring and does not claim a Tau Core validation.

## Audited Branch Equation

The tested branch equation is the B-sector gradient row of:

```text
S_total = S_scaffold + S_rest
F_B = D_B S_total
```

At the origin candidate:

```text
Phi0=0; P0=0; B0=0
```

the linear branch equation is stationary. The one-dimensional branch
linearization is computable:

```text
L_B_red = -0.3015113445777636
```

## Key Result

The audit finds that the direct parent forcing term is:

```text
D_Phi_F_B = 0.0
```

while the projection-mediated coupling is:

```text
D_P_F_B = -0.6030226891555273
```

So the current scaffold gives a computable branch row and a projection-mediated
path, but not a direct `D_Phi F_B` forcing term. The next step must therefore
either declare the mediated chain explicitly or derive a nonzero direct forcing
from the parent action.

## Stability Boundary

The active Hessian minimum eigenvalue is:

```text
-0.8168772564552302
```

Thus this audit does not prove full active stability.

## Claim Boundary

Allowed statement:

> The existing target-blind action gives a partial branch-equation completion:
> `F_B` and `L_B_red` are computable, while the parent forcing remains mediated
> or incomplete.

Forbidden statement:

> The reduced branch-Jacobian is complete, empirical scoring is authorized, or
> Tau Core has been validated.
