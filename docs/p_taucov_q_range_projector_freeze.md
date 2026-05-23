# P-TauCov Q-Range Projector Freeze

Freeze ID: `P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_v1`

Status:

`P_TAUCOV_Q_RANGE_PROJECTOR_FREEZE_PASS_NO_SCORING`

## Purpose

This artifact freezes the orthogonal projector onto the range of the common
cleaner:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
Q_range = U_active U_active^T
```

where active eigenvectors are selected from the spectrum of `Q_clean` using the
predeclared threshold:

```text
eigenvalue > 1e-10
```

It does not construct a Tau candidate and does not authorize empirical scoring.

## Metrics

| Quantity | Value |
|---|---:|
| rows | `36` |
| active rank | `31` |
| trace `Q_range` | `30.99999999999999` |
| min active eigenvalue | `0.09143894881209928` |
| max inactive eigenvalue | `1.0608030265852466e-15` |
| `Q_clean` symmetry error | `1.6534746151173284e-15` |
| `Q_range` symmetry error | `0.0` |
| `Q_range` idempotence error | `5.154299882972685e-15` |
| passed gates | `5 / 5` |

## Claim Boundary

Allowed statement:

> The orthogonal range projector of the frozen common cleaner has been constructed without target residual scoring.

Forbidden statement:

> The Q-range projector validates Tau Core, constructs a scoreable candidate, or authorizes empirical scoring.
