# P-TauCov Linear Specificity Prescore

Status: evaluated / strict-linear candidate not frozen / P-TauCov scoring not
authorized.

The target-blind strict-linear packet was evaluated using only the frozen
coordinate basis, reference-domain projectors, source objects, and derived
linear objects.

## Linear Response Convention

```text
T_tau = A_Phi + A_B L0_B^+ R_B
delta_C_tau = T_tau T_tau^T
```

Under the frozen minimal packet:

```text
A_Phi = P_red
A_B   = P_red
L0_B  = P_red
R_B   = -P_red
```

therefore the direct morphology term and branch-mediated term cancel in the
retained reduced domain. The resulting linear response is the zero baseline:

```text
||T_tau||_F = 0
```

## Result

```text
Status: FAIL_STRICT_LINEAR_REJECTED
MetricsPassed: 2/6
LinearCandidateFrozen: false
PTauCovScoringAuthorized: false
```

This is a useful negative gate. The strictly linear minimal candidate is too
degenerate to freeze as a Tau-specific branch/projection/covariance response.

## Next Step

```text
freeze_minimal_nonzero_lambda_B_or_epsilon_P_model
```

The next model must be declared before empirical scoring and must use either a
minimal nonzero branch backreaction term or a minimal nonzero projection-response
term.

## Claim Boundary

Allowed statement:

```text
The strict-linear minimal P-TauCov packet fails the target-blind specificity
audit and is not frozen for scoring.
```

Forbidden statement:

```text
The specificity audit produced an empirical Tau signal or authorized P-TauCov
scoring.
```
