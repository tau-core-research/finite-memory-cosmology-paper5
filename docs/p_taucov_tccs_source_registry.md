# P-TauCov TCCS Source Registry

Freeze ID: `P_TAUCOV_TCCS_SOURCE_REGISTRY_v1`

Status:

`P_TAUCOV_TCCS_SOURCE_REGISTRY_READY_FOR_OBJECT_PREFLIGHT_NO_SCORING`

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

The TCCS support components are now frozen enough for object-construction preflight. This still does not authorize scoring.

## Component Status

| Component | Status | Blocking issue |
|---|---|---|
| `L_B_red` | `AVAILABLE_FOR_OBJECT_PREFLIGHT` | must pass object-construction gates |
| `P_morph` | `FROZEN_OPERATOR_CONVENTION_AVAILABLE` | none for preflight |
| `Pi_perp` | `FROZEN_MATRIX_AVAILABLE` | none for preflight |
| `Pi_bal` | `AVAILABLE` | must be rechecked after object construction |
| `J_tau` | `FROZEN_ANCHOR_CANDIDATE_AVAILABLE` | none for preflight |
| `TCCS_OBJECT` | `NOT_CONSTRUCTED_PREFLIGHT_READY` | next step is object-construction preflight |

## Claim Boundary

Allowed statement:

> The TCCS source registry identifies the required parent-side sources and authorizes object-construction preflight without scoring.

Forbidden statement:

> A TCCS object has been built, score-authorized, or shown to carry a Tau signal.
