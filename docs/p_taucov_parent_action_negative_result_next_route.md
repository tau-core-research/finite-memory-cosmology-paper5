# P-TauCov Parent-Action Negative Result And Next Route

Status: negative primary scorecard / no survival claim / route-selection note.

The first authorized parent-action primary covariance scorecard is negative:

```text
PrimaryOOSDeltaNLL_BaselineMinusKernel = -0.2996400323571766
```

This means the minimal two-coordinate PSD covariance lift,

```math
D_M C[T] = \frac{TT^{\mathsf T}}{\|TT^{\mathsf T}\|_F},
```

does not improve the primary out-of-sample covariance likelihood over the
baseline.

## What This Does Mean

The full parent-action protocol can be frozen, authorized, executed, and
interpreted without target-dependent tuning.

The minimal parent-action PSD lift is too weak or too compressed for the
registered empirical covariance target.

The result is compatible with the earlier lesson from P5C-v3: a local
orientation/covariance anomaly can exist while the simple global PSD
covariance deformation fails.

## What This Does Not Mean

This is not a Tau Core falsification.

This is not a failure of all branch-localized covariance-response tests.

This is not evidence for a richer model unless that richer model is frozen
before scoring.

## Allowed Next Route

The next route should not be an unconstrained v4 score search. It should be a
new predeclared model class that addresses the observed failure mode:

```text
minimal global PSD lift too compressed
-> require branch-localized or block-structured response
-> freeze support and null policy before scoring
```

Allowed candidate classes:

1. Branch-localized PSD response with frozen branch support.
2. Signed response protocol with a separate signed-operator contrast statistic.
3. Low-rank multi-channel response if each channel is parent-action derived and
   the df penalty is frozen before scoring.

Forbidden candidate classes:

1. Any kernel chosen because it improves the just-observed negative score.
2. Any secondary diagnostic promoted to survival after primary failure.
3. Any family-localized rescue without a held-out branch-support rule.

## Current Best Status

```text
P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_NEGATIVE_NO_SURVIVAL_CLAIM
```

The protocol infrastructure is strong. The minimal two-coordinate PSD candidate
is not.
