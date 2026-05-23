# P-TauCov Epsilon-P3 Model Packet

Status: target-blind `epsilon_P/P3` model packet / specificity metrics
authorized / P-TauCov scoring not authorized.

This packet is the core-mixing successor to the support-entropy-failed `P2`
route. It does not overwrite the P1/P2 packets or the strict-linear negative
baseline.

## Frozen Model

```text
lambda_B = 0
epsilon_P = 1
P_epsilon = P0 + epsilon_P * P3
```

The unit value `epsilon_P = 1` is a normalization convention, not a fitted
amplitude. It is allowed because `P3` was frozen with unit Frobenius norm before
any empirical P-TauCov scoring.

## Boundary

Allowed statement:

```text
The target-blind epsilon-P3 model packet is frozen for specificity auditing.
```

Forbidden statement:

```text
The epsilon-P3 packet has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
