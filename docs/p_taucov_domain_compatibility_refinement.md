# P-TauCov Domain-Compatibility Refinement

Freeze ID: `P_TAUCOV_DOMAIN_COMPATIBILITY_REFINEMENT_v1`

Status:

`P_TAUCOV_DOMAIN_COMPATIBILITY_REFINEMENT_AUDITED_CLEANERS_COMPATIBLE_NO_SCORING`

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

The original failure mode was:

```text
nonzero transfer-curvature
-> almost no norm retained after branch balancing
-> large projection leakage after the full construction
```

This initially left open whether `Pi_perp` and `Pi_bal` were themselves
incompatible operations. The follow-up audit now checks that directly.

## Follow-Up Audit Result

The frozen cleaner pair passes the target-blind compatibility audit:

[`p_taucov_domain_compatibility_audit.md`](p_taucov_domain_compatibility_audit.md)

Key metrics:

| Quantity | Value |
|---|---:|
| relative cleaner commutator norm | `0.012555596849346958` |
| relative order-difference norm | `0.011250508343623337` |
| rank `Pi_perp` | `34` |
| rank `Pi_bal` | `31` |
| rank common cleaner `Pi_bal Pi_perp Pi_bal` | `31` |
| passed gates | `7 / 7` |

This changes the interpretation. The transfer-curvature preflight did not fail
because the two cleaning operators are globally incompatible. It failed because
the current `K_curv` object has too little energy in the common clean subspace
and too much leakage after the full construction.

In short:

```text
cleaning geometry: acceptable at score-space level
current transfer-curvature object: not aligned with the clean Tau subspace
```

## Required Condition

A future Tau-specific covariance object must satisfy one of two conditions.

### Route A: Compatible Cleaning Operators

`Pi_perp` and `Pi_bal` remain derived from the same parent metric or
self-adjoint-domain structure, and the candidate curvature has real support in
their common clean subspace:

```text
norm(Pi_bal Pi_perp K_curv Pi_perp Pi_bal) / norm(K_curv) >= frozen threshold
```

with low projection leakage. The cleaner-pair audit suggests this route remains
open; the missing ingredient is a better parent-side curvature object, not a
new arbitrary cleaner.

The next protocol-level expression of this requirement is:

[`p_taucov_common_clean_subspace_support_protocol.md`](p_taucov_common_clean_subspace_support_protocol.md)

### Route B: Non-Commutation As Observable

If a future parent geometry produces materially non-commuting cleaners, their
non-commutation must be declared as the observable itself before scoring:

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
Also do not blame the current transfer-curvature failure on cleaner
incompatibility: the dedicated audit says the cleaner pair is acceptable.

## Claim Boundary

Allowed statement:

> The TCCS failures sharpen the P-TauCov theory: the frozen cleaners are mutually compatible, so the next object must place genuine parent curvature into their common clean subspace.

Forbidden statement:

> The domain-compatibility refinement validates a Tau signal or authorizes empirical scoring.
