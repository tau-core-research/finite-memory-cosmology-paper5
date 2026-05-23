# P-TauCov Next Route After P4 Preflight

Status: route decision note / no new candidate / no scoring authorization.

The P4 morphology-orthogonal candidate preflight failed before empirical
scoring:

```text
gates passed                         = 3/6
tau norm retained after projection   = 0.8309489698388166
kernel correlation with morphology   = 0.8893567053441822
projection-null abs correlation      = 0.8565316433152965
shuffled-support abs correlation     = 0.665272141460644
max family energy share              = 0.19882475456411108
max clock energy share               = 0.16971387889717798
```

The useful information is that family/clock dominance is not the active
blocker after morphology projection. The active blocker is structural: the
candidate remains too close to generic morphology/projection covariance.

## Interpretation

The current TauCov construction is not yet Tau-specific enough. It produces a
real covariance-like response, but the response is still explainable by a
generic morphology/projection deformation. Therefore, another scorecard run
would be premature.

## Forbidden Next Step

Do not tune a P4 or v4 candidate against the failed gates by changing thresholds
or support after observing these diagnostics.

## Allowed Next Routes

### Route R1: derive a non-morphology Tau operator

Build the response from a parent-structure commutator or Hessian term that is
orthogonal to both declared morphology axes by construction:

```text
T_tau_specific ~ [P_projection, L_tau] or Hessian_cross(Phi, B)
```

This route is theory-first. It can only be tested after the operator is frozen
from the parent equations.

### Route R2: introduce an independent external morphology basis

The present morphology basis is internal to the tau-coordinate packet. A
stronger null would use an independently declared external morphology basis.
This route is data-protocol-first and requires a new source packet before any
candidate is built.

### Route R3: change claim boundary to morphology-mediated Tau response

If the theory predicts that Tau response must appear through morphology, then
the claim must be weakened and renamed:

```text
Tau-mediated morphology covariance response
```

That would no longer be a clean Tau-specific residual channel. It would require
different success criteria and cannot inherit the current P-TauCov survival
gate.

## Recommended Next Step

Route R1 is the cleanest Tau-specific path. The next artifact should be:

```text
docs/p_taucov_parent_hessian_commutator_route.md
```

It should specify which parent operator term could produce a response that is
not a morphology-null duplicate, before any new matrix is generated.
