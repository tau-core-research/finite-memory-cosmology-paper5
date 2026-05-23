# P-TauCov Projection-Essentiality Global Constraint Origin

Status: parent-structure constraint origin / no empirical scorecard / no
survival claim.

The local action-selection theorem fixes the projection-essential normal form
under C1-C7. This document records how C1-C7 are intended to arise from the
broader Tau-response parent structure rather than remaining arbitrary local
rules.

## Parent Principles

| Principle | Parent-level role | Local constraint implied |
| --- | --- | --- |
| G1 Local stationary expansion | Work near a frozen branch/reference state and keep the first nontrivial Hessian sector. | C1 quadratic local normal form |
| G2 Observable-sector separation | The witness sector may use only parent source, branch response, and projection response coordinates. Parent morphology is a null competitor, not an input. | C2 no `M` coordinate and no target residual input |
| G3 Projection is mediator, not stored energy | Pure projection amplitude is gauge-like in this witness sector and cannot carry a self-energy term. | C3 no `P^2` |
| G4 Source is external perturbation, not fitted amplitude | Pure source self-energy is absorbed into the source normalization and cannot enter the witness. | C4 no `Phi^2` |
| G5 Reduced branch metric fixes branch scale | The reduced branch coordinate is normalized by its quadratic counterterm. | C5 `-1/2 B^2` |
| G6 Relaxed branch follows projection with opposite orientation | The reduced stationary branch equation gives `B_* = -2P`. | C6 branch relaxation orientation |
| G7 Unit source-projection response | The projection-source coupling fixes the remaining source scale. | C7 `-P Phi` |

## Local Consequence

With these parent principles, the admissible local potential is:

```math
V_{\rm PE}(\Phi,B,P)
=
-2PB - P\Phi - \frac{1}{2}B^2 .
```

The route is:

```text
parent stationary expansion
-> reduced branch metric
-> projection as mediator
-> no self-energy witness constraints
-> unique local projection-essential normal form
-> Hessian witness
```

## Claim Boundary

Allowed:

```text
C1-C7 now have a declared parent-structure origin route.
```

Forbidden:

```text
C1-C7 have been derived from a final microscopic Tau Core action.
```

## Remaining Gate

The remaining hard gate is to replace the principle table by an explicit global
parent action whose stationary expansion produces G1-G7.
