# P-TauCov Domain-Compatibility Refinement

Freeze ID: `P_TAUCOV_DOMAIN_COMPATIBILITY_REFINEMENT_v1`

Status:

`P_TAUCOV_DOMAIN_COMPATIBILITY_REFINEMENT_REQUIRED_NO_SCORING`

## Motivation

The TCCS sequence produced two useful structural results:

1. the double-sided projected commutator is algebraically blocked; and
2. the no-go-corrected transfer-curvature object is nonzero but does not survive
   the current branch/perp cleanliness gates.

Together these results indicate that the missing object is not another
target-blind shape kernel. The missing object is a parent-domain rule.

## Refinement

The projection-orthogonal complement and the branch-balanced subspace must be
defined from a common parent structure:

```text
parent inner product / metric / self-adjoint domain
-> Pi_perp
-> Pi_bal
-> score-space covariance object
```

The current failure mode is:

```text
nonzero transfer-curvature
-> almost no norm retained after branch balancing
-> large projection leakage after the full construction
```

This means the present `Pi_perp` and `Pi_bal` definitions are not yet known to be
compatible operations in the same parent geometry.

## Required Condition

A future Tau-specific covariance object must satisfy one of two conditions.

### Route A: Compatible Cleaning Operators

`Pi_perp` and `Pi_bal` are derived from the same parent metric or
self-adjoint-domain structure, and the cleaned curvature remains nonzero:

```text
norm(Pi_bal Pi_perp K_curv Pi_perp Pi_bal) / norm(K_curv) >= frozen threshold
```

with low projection leakage.

### Route B: Non-Commutation As Observable

If `Pi_perp` and `Pi_bal` do not commute, their non-commutation must be declared
as the observable itself before scoring:

```text
[Pi_bal, Pi_perp] K_curv
```

or an equivalent parent-domain curvature term.

This route is only valid if the object is frozen before target residual scoring
and is tested against morphology-null, projection-null, family-localized,
shuffle, and generic smooth baselines.

## Forbidden Move

Do not treat projection cleaning and branch balancing as arbitrary sequential
post-processing operations chosen after seeing which version scores better.

## Claim Boundary

Allowed statement:

> The TCCS failures sharpen the P-TauCov theory by requiring a common parent-domain rule for projection orthogonality and branch balance.

Forbidden statement:

> The domain-compatibility refinement validates a Tau signal or authorizes empirical scoring.
