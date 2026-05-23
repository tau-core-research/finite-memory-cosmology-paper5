# P-TauCov Common-Clean-Subspace Support Protocol

Freeze ID: `P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_PROTOCOL_v1`

Status:

`P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING`

## Motivation

The TCCS route now has three structural lessons:

1. the double-sided projected commutator is algebraically blocked;
2. the no-go-corrected transfer-curvature object is nonzero but fails the
   branch/perp object gate; and
3. the frozen `Pi_perp` and `Pi_bal` cleaners are mutually compatible at
   score-space level.

Therefore the next blocker is no longer the cleaner geometry. The blocker is
the absence of a parent-side curvature source whose support is native to the
common clean subspace.

## Common Clean Subspace

Define the frozen common cleaner:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
```

or its symmetrized equivalent if a future parent-domain derivation requires it.

The current audit shows that this subspace is nontrivial:

```text
rank(Q_clean) = 31
```

## Required Candidate Form

A future parent-side Tau covariance candidate must have the form:

```text
K_tau = Q_clean K_parent Q_clean
```

where `K_parent` is derived before scoring from one of:

1. parent Hessian curvature;
2. parent-domain boundary curvature;
3. reduced branch-response curvature;
4. declared non-commutation curvature between parent-domain operators.

It may not be chosen from target residual alignment.

## Pre-Score Support Gates

Before empirical scoring is authorized, the candidate must pass:

| Gate | Requirement |
|---|---|
| CCS-G1 | `norm(K_parent) > 0` |
| CCS-G2 | `norm(Q_clean K_parent Q_clean) / norm(K_parent) >= frozen threshold` |
| CCS-G3 | projection leakage below frozen threshold |
| CCS-G4 | max family energy share below frozen threshold |
| CCS-G5 | diagonal energy share below frozen threshold |
| CCS-G6 | morphology-null and projection-null correlations below frozen thresholds |
| CCS-G7 | all hashes and thresholds frozen before target scoring |

The initial threshold suggested by the failed transfer-curvature preflight is:

```text
support_retention >= 0.20
```

This is not a physical constant. It is a pre-score admissibility threshold for
whether an object is worth scoring at all.

## Forbidden Move

Do not build another scorecard until a candidate passes common-clean-subspace
support preflight. A weak object cannot be rescued by changing scoring mode.

## Claim Boundary

Allowed statement:

> The next P-TauCov object must be a parent-derived curvature with non-negligible support in the frozen common clean subspace.

Forbidden statement:

> The common-clean-subspace protocol validates Tau Core or authorizes empirical scoring.
