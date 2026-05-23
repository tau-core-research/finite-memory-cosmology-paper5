# P-TauCov Q-Native Route Registry

Freeze ID: `P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_v1`

Status:

`P_TAUCOV_Q_NATIVE_ROUTE_REGISTRY_DEFINED_NO_OBJECT_NO_SCORING`

## Purpose

This registry converts the Q-native parent-curvature derivation gate into a
machine-readable route list. It defines possible source routes only. It does
not construct an object, authorize support audit, or authorize scoring.

## Routes

| Route | Source expression | Main open gate |
|---|---|---|
| `QN_ROUTE_1_CONSTRAINED_HESSIAN_RESIDUE` | `R_parent = Hessian(S_parent)_reduced - Proj_forbidden(Hessian(S_parent)_reduced)` | `derive forbidden projection and reduced Hessian from parent action before scoring` |
| `QN_ROUTE_2_BOUNDARY_CURVATURE` | `R_parent = B_boundary^T B_boundary` | `derive boundary operator from parent domain, defect, or quotient sector` |
| `QN_ROUTE_3_COMPATIBILITY_CURVATURE` | `R_parent = [D_parent,Q_clean]^T [D_parent,Q_clean]` | `freeze D_parent from parent-domain operator, not empirical covariance` |
| `QN_ROUTE_4_BRANCH_RESPONSE_CURVATURE` | `R_parent = J_response^T J_response` | `derive J_response from reduced branch equation and map it into Q_clean` |

## Claim Boundary

Allowed statement:

> Four Q-native parent-curvature source routes have been registered as no-scoring derivation options.

Forbidden statement:

> Any registered route has produced a Tau signal, a scoreable object, or empirical survival.

## Priority Note

The current recommended route is recorded in:

[`p_taucov_q_native_route_priority_note.md`](p_taucov_q_native_route_priority_note.md)
