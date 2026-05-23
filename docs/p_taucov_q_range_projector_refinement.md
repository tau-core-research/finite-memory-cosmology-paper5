# P-TauCov Q-Range Projector Refinement

Freeze ID: `P_TAUCOV_Q_RANGE_PROJECTOR_REFINEMENT_v1`

Status:

`P_TAUCOV_Q_RANGE_PROJECTOR_REFINEMENT_REQUIRED_NO_OBJECT_NO_SCORING`

## Motivation

The common cleaner is:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
```

It is useful as a cleaning operator, but it should not automatically be treated
as an exact orthogonal projector. The minimal Q-native branch-response
preflight exposed this issue through a large closure error:

```text
norm(Q_clean K_Q Q_clean - K_Q) / norm(K_Q) = 0.7888917899683725
```

Therefore the next mathematical refinement is to separate:

```text
Q_clean  = cleaner / positive compression
Q_range  = orthogonal projector onto range(Q_clean)
```

## Required Construction

Before another Q-native object is tested, freeze:

```text
Q_range = U_active U_active^T
```

where `U_active` are eigenvectors of the symmetric common cleaner with
eigenvalues above a frozen numerical threshold.

The threshold must be declared before object construction.

## Why This Matters

A candidate should be native to the clean subspace:

```text
Q_range K_Q Q_range = K_Q
```

not necessarily fixed by repeated multiplication with the non-idempotent
cleaning compression `Q_clean`.

This avoids confusing two different operations:

1. cleaning/attenuation by `Q_clean`;
2. subspace membership under `Q_range`.

## Forbidden Move

Do not choose the eigenvalue threshold after inspecting empirical scores. The
range projector must be frozen from the cleaner spectrum alone.

## Claim Boundary

Allowed statement:

> The Q-native branch-response failure identifies the need to freeze an orthogonal range projector for the common clean subspace.

Forbidden statement:

> The Q-range refinement validates Tau Core, constructs a scoreable object, or authorizes empirical scoring.
