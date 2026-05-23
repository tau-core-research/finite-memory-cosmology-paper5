# P-TauCov Q-Range Projector Refinement

Freeze ID: `P_TAUCOV_Q_RANGE_PROJECTOR_REFINEMENT_v1`

Status:

`P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_PASS_NO_SCORING`

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

## Freeze Result

The range projector has now been frozen:

[`p_taucov_q_range_projector_freeze.md`](p_taucov_q_range_projector_freeze.md)

Result:

```text
P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_PASS_NO_SCORING
```

Key metrics:

| Quantity | Value |
|---|---:|
| active rank | `31` |
| min active eigenvalue | `0.09143894881209928` |
| max inactive eigenvalue | `1.0608030265852466e-15` |
| idempotence error | `5.154299882972685e-15` |

This is a stable separation between the clean-subspace range and the numerical
null complement.

## Branch-Response Retest

The minimal branch-response contrast was retested with `Q_range`:

[`p_taucov_q_range_branch_response_preflight.md`](p_taucov_q_range_branch_response_preflight.md)

Result:

```text
P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_FAIL_NO_SCORING
```

Key number:

```text
QRangeRetention = 9.11401163254385e-16
```

Thus the previous failure was not merely a consequence of using non-idempotent
`Q_clean`. The simple `B - Phi` contrast is almost entirely outside the frozen
clean subspace.

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
