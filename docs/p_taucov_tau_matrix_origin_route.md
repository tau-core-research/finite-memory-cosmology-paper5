# P-TauCov Tau Matrix-Origin Route

Status: theory-origin route / no concrete packet / no metric evaluation / no
scoring authorization.

This document states how the required linear packet matrices must arise from
the Tau-side response model. It does not provide the matrices themselves.

## Origin Routes

| Matrix | Tau-side origin | Formal route |
| --- | --- | --- |
| `L0_B` | reduced branch Hessian / branch-sector linearization | `L0_B = P_red D_B F_B|_(Phi,B_*) P_red` |
| `R_B` | parent-to-branch forcing | `R_B = - P_red D_Phi F_B|_(Phi,B_*)` |
| `P_red` | reduced admissible branch domain | `P_red = I - P_null - P_gauge - P_forbidden` |
| `A_Phi` | direct parent morphology derivative | `A_Phi = D_Phi M_parent|_(Phi,B_*)` |
| `A_B` | branch morphology derivative | `A_B = D_B M_parent|_(Phi,B_*)` |
| `P0` | fixed morphology projection | `P0 = P_morph(Phi_0,B_*(Phi_0))` or declared coordinate projection |

## What This Achieves

This route prevents the matrices from being arbitrary. They are not fit
parameters and not score-selected kernels. They must be derivatives or
projections of declared Tau-side objects.

## What Is Still Missing

The route still requires explicit, target-blind definitions of:

```text
F_B
M_parent
P_morph
branch null/gauge basis
reference state Phi_0
```

Without those objects, no concrete matrix packet is authorized.

## Claim Boundary

Allowed statement:

```text
The linear packet matrices now have a declared Tau-side origin route.
```

Forbidden statement:

```text
The linear packet matrices have been derived or frozen.
```
