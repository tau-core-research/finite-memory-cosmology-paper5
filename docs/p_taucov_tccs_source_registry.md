# P-TauCov TCCS Source Registry

Freeze ID: `P_TAUCOV_TCCS_SOURCE_REGISTRY_v1`

Status:

`P_TAUCOV_TCCS_SOURCE_REGISTRY_READY_OBJECT_BLOCKED`

## Purpose

This registry keeps the Tau Commutator Curvature Signature route target-blind. It does not build a TCCS object and does not authorize scoring. It only declares which frozen or missing sources would be needed before the object

```text
T_tau = Normalize(Pi_bal Pi_perp Orient_+([L_B_red, P_morph]; J_tau) Pi_perp Pi_bal)
```

can be constructed.

## Why This Registry Is Needed

The previous parent-Hessian commutator attempt was informative but not sufficient:

```text
previous morphology-null=0.1686357268015766; projection-null=0.7337111972818574
```

Thus the next object must be explicitly projection-orthogonal, branch-balanced, and orientation-anchored before any empirical score is touched.

## Component Status

| Component | Status | Blocking issue |
|---|---|---|
| `L_B_red` | `AVAILABLE_BUT_NOT_ACCEPTED_FOR_TCCS` | prior commutator source failed projection-null separation |
| `P_morph` | `AVAILABLE_AS_MORPHOLOGY_BASIS_NOT_YET_OPERATOR_FREEZE` | needs explicit operator convention |
| `Pi_perp` | `PARTIAL_SOURCE_AVAILABLE_NOT_ASSEMBLED` | projection-null and morphology-null bases must be combined |
| `Pi_bal` | `AVAILABLE` | must be rechecked after object construction |
| `J_tau` | `MISSING_REQUIRED_SOURCE` | target-blind orientation anchor is not frozen |
| `TCCS_OBJECT` | `BLOCKED` | no object until all source components are frozen |

## Claim Boundary

Allowed statement:

> The TCCS source registry identifies the required parent-side sources and shows that object construction is still blocked.

Forbidden statement:

> A TCCS object has been built, score-authorized, or shown to carry a Tau signal.
