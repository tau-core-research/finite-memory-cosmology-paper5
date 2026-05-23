# P-TauCov Reduced Branch-Jacobian Source Spec

Freeze ID: `P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_v1`

Status:

`P_TAUCOV_REDUCED_BRANCH_JACOBIAN_SOURCE_SPEC_BLOCKED_NO_OBJECT_NO_SCORING`

## Purpose

This source spec records the operators required before a true Q-native
branch-response Jacobian can be constructed:

```text
J_response = Q_range D_B M_proj (L_B^red)^(-1) D_Phi F_B
```

It does not construct `J_response`, does not build `K_Q`, and does not
authorize empirical scoring.

## Source Objects

| Object | Status | Required expression | Blocks Jacobian |
|---|---|---|---|
| `Q_range` | `FROZEN_AVAILABLE` | `Q_range = U_active U_active^T from spectrum(Q_clean)` | `False` |
| `L_B_red` | `MISSING_CONCRETE_OPERATOR` | `L_B_red = P_red D_B F_B|_(Phi0,B*) P_red` | `True` |
| `D_Phi_F_B` | `MISSING_CONCRETE_OPERATOR` | `D_Phi_F_B = D_Phi F_B|_(Phi0,B*)` | `True` |
| `D_B_M_proj` | `BLOCKED_BY_M_PARENT_AND_P_MORPH` | `D_B_M_proj = D_B(P_morph M_parent)|_(Phi0,B*)` | `True` |
| `P_red` | `PARTIALLY_RESOLVED_BY_FULL_ACTION_DOMAIN_PACKET` | `P_red = I - P_null - P_gauge - P_forbidden` | `False` |
| `ReferenceState` | `POLICY_DECLARED_VALUE_NOT_SOLVED` | `(Phi0,B*(Phi0)) with F_B(Phi0,B*)=0` | `True` |
| `ForbiddenCoordinateContrast` | `FORBIDDEN_BY_QRANGE_RETENTION_FAIL` | `v_branch != B_BRANCH_RESPONSE - PHI_PARENT_SOURCE` | `False` |

## Key Result

`Q_range` is now frozen and available. `P_red` is also no longer a primary
blocker because the full-action-domain packet supplies a target-blind
active/reduced projector.

The actual reduced branch-Jacobian sources remain blocked:

```text
L_B_red
D_Phi_F_B
D_B_M_proj
ReferenceState
```

The shortcut:

```text
B_BRANCH_RESPONSE - PHI_PARENT_SOURCE
```

is explicitly forbidden by the Q-range retention failure.

Blocker-resolution audit:

[`p_taucov_reduced_branch_jacobian_blocker_resolution.md`](p_taucov_reduced_branch_jacobian_blocker_resolution.md)

## Claim Boundary

Allowed statement:

> The required source objects for a reduced branch-Jacobian have been enumerated after the Q-range failure.

Forbidden statement:

> The reduced branch-Jacobian has been constructed, scored, or shown to validate Tau Core.
