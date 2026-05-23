# P-TauCov TCCS Source Registry

Freeze ID: `P_TAUCOV_TCCS_SOURCE_REGISTRY_v1`

Status:

`P_TAUCOV_TCCS_SOURCE_REGISTRY_OBJECT_PREFLIGHT_COMPLETE_NO_SCORING`

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

The TCCS support components were frozen enough for object-construction
preflight. The original double-sided object failed structurally, and the
no-go-corrected transfer-curvature object also failed the full branch/perp
cleanliness gate. This still does not authorize scoring.

## Component Status

| Component | Status | Blocking issue |
|---|---|---|
| `L_B_red` | `AVAILABLE_FOR_OBJECT_PREFLIGHT` | must pass object-construction gates |
| `P_morph` | `FROZEN_OPERATOR_CONVENTION_AVAILABLE` | none for preflight |
| `Pi_perp` | `FROZEN_MATRIX_AVAILABLE` | none for preflight |
| `Pi_bal` | `AVAILABLE_BUT_DOMAIN_COMPATIBILITY_REQUIRED` | must be co-defined with `Pi_perp` in a common parent domain |
| `J_tau` | `FROZEN_ANCHOR_CANDIDATE_AVAILABLE` | none for preflight |
| `TCCS_OBJECT` | `PREFLIGHT_FAILED_NO_SCORING` | double-sided object collapses after `Pi_perp`/`Pi_bal` |
| `TCCS_TRANSFER_CURVATURE` | `PREFLIGHT_FAILED_NO_SCORING` | nonzero raw curvature, but weak retained norm and high leakage |
| `DOMAIN_COMPATIBILITY` | `REQUIRED_NEXT_THEORY_GATE` | common metric/domain needed for `Pi_perp` and `Pi_bal` |

## Theory Feedback

The source registry now identifies a parent-theory requirement rather than a
missing data source:

```text
Pi_perp and Pi_bal must be derived from the same parent metric/domain
```

or their non-commutation must be declared as a frozen observable before any
empirical score is inspected.

Detailed refinement:

[`p_taucov_domain_compatibility_refinement.md`](p_taucov_domain_compatibility_refinement.md)

## Claim Boundary

Allowed statement:

> The TCCS source registry identifies the required parent-side sources and authorizes object-construction preflight without scoring.

Forbidden statement:

> A TCCS object has been score-authorized or shown to carry a Tau signal.
