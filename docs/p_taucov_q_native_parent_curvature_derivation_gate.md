# P-TauCov Q-Native Parent Curvature Derivation Gate

Freeze ID: `P_TAUCOV_Q_NATIVE_PARENT_CURVATURE_DERIVATION_GATE_v1`

Status:

`P_TAUCOV_Q_NATIVE_PARENT_CURVATURE_DERIVATION_GATE_DEFINED_NO_OBJECT_NO_SCORING`

## Motivation

The common-clean-subspace support audit found no passing candidate among the
existing parent-curvature inventory. The best retained support was only:

```text
0.00836108135986166
```

for `TCCS_TRANSFER_CURVATURE`, far below the frozen preflight threshold:

```text
support_retention >= 0.20
```

This means the next object cannot be obtained by taking an old parent/Hessian
matrix and cleaning it after the fact. The next object must be native to the
common clean subspace from the start.

## Target Object

Let:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
```

The next admissible parent-curvature candidate must be generated as:

```text
K_Q = Q_clean R_parent Q_clean
```

where `R_parent` is not selected from target residual behavior. It must come
from a declared parent-side structure.

The stronger target is:

```text
Q_clean K_Q Q_clean = K_Q
```

up to numerical tolerance.

## Candidate Parent Sources

A Q-native curvature source may be derived from one of these routes.

The machine-readable route registry is:

[`p_taucov_q_native_route_registry.md`](p_taucov_q_native_route_registry.md)

### Route 1: Constrained Hessian Residue

Start from a parent action:

```text
S_parent[Phi, B, M, P]
```

and derive a reduced Hessian residue after eliminating nuisance directions:

```text
R_parent = Hessian(S_parent)_reduced - Proj_forbidden(Hessian(S_parent)_reduced)
```

The residue must be defined before scoring and must not use target residuals.

### Route 2: Boundary Curvature

If the parent domain has a boundary, defect, or quotient sector, derive:

```text
R_parent = B_boundary^T B_boundary
```

or a signed boundary pairing whose PSD form is frozen before scoring.

This route is admissible only if the boundary operator is fixed by the parent
domain and not fitted to empirical covariance.

### Route 3: Compatibility Curvature

If parent-domain projections are nontrivial, define curvature from their
failure to commute:

```text
R_parent = [D_parent, Q_clean]^T [D_parent, Q_clean]
```

where `D_parent` is a declared parent-domain operator. This is allowed only if
`D_parent` is frozen before target scoring.

### Route 4: Branch-Response Curvature

If branch response is governed by:

```text
L_B^red delta B = -D_Phi F_B[delta Phi]
```

then the Q-native object must be derived from the reduced response itself:

```text
R_parent = J_response^T J_response
```

where `J_response` is the frozen Jacobian mapping parent perturbations into the
common clean subspace.

## Required Pre-Score Gates

Before any scoring manifest is allowed, the Q-native candidate must pass:

| Gate | Requirement |
|---|---|
| QN-G1 | parent source declared before scoring |
| QN-G2 | `K_Q` nonzero |
| QN-G3 | `norm(Q_clean K_Q Q_clean - K_Q) / norm(K_Q) <= 1e-10` |
| QN-G4 | support retention relative to declared `R_parent` is at least `0.20` |
| QN-G5 | projection leakage below frozen threshold |
| QN-G6 | max family energy share below frozen threshold |
| QN-G7 | diagonal energy share below frozen threshold |
| QN-G8 | morphology-null and projection-null correlations below frozen thresholds |
| QN-G9 | hashes, thresholds, and source route frozen before target scoring |

## What This Changes

Earlier candidates were built first and cleaned later:

```text
old object -> Q_clean old object Q_clean
```

The support audit shows this is too weak. The new requirement is:

```text
parent source -> Q-native curvature -> support audit -> only then scoring manifest
```

## Forbidden Move

Do not tune a new curvature source by maximizing empirical score. The source
route, operator, thresholds, and hashes must be frozen before any target
residual score is inspected.

## Claim Boundary

Allowed statement:

> The failed support audit defines a sharper next gate: a future P-TauCov object must be Q-native, not merely cleaned after construction.

Forbidden statement:

> A Q-native derivation gate validates Tau Core, authorizes scoring, or proves a physical covariance response.
