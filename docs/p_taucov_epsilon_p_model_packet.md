# P-TauCov Epsilon-P Model Packet

Status: target-blind `epsilon_P` model packet / specificity metrics authorized /
P-TauCov scoring not authorized.

This packet is the first minimal nonzero model after the strict-linear negative
gate. The strict-linear packet is preserved as a failed baseline; this packet
does not overwrite it.

## Frozen Model

```text
lambda_B = 0
epsilon_P = 1
P_epsilon = P0 + epsilon_P * P1
```

The unit value `epsilon_P = 1` is a normalization convention, not a fitted
amplitude. It is allowed because `P1` was frozen with unit Frobenius norm before
any empirical P-TauCov scoring.

## Why This Is The Next Model

The strict-linear candidate failed because:

```text
T_tau = A_Phi + A_B L0_B^+ R_B = 0
```

The minimal nonzero repair is therefore projection-side rather than
branch-covariance-side:

```text
P1: parent source -> projection coordinate -> morphology coordinate
```

## Claim Boundary

Allowed statement:

```text
The target-blind epsilon_P model packet is frozen and may be used for
specificity auditing.
```

Forbidden statement:

```text
The epsilon_P packet has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
