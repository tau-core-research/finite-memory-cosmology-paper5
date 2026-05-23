# P-TauCov Epsilon-P Specificity Prescore

Status: evaluated / epsilon-P candidate not yet frozen / P-TauCov scoring not
authorized.

This prescore evaluates the target-blind epsilon-P model packet:

```text
T_tau_epsilon = A_Phi + A_B L0_B^+ R_B + epsilon_P P1
delta_C_tau = T_tau_epsilon T_tau_epsilon^T
```

The strict-linear base term cancels, so the active nonzero structure comes from
the frozen `P1` projection-response operator.

## Result

```text
Status: FAIL_EPSILON_P_NOT_SPECIFIC
MetricsPassed: 5/6
||T_tau_epsilon||_F = 1
PTauCovScoringAuthorized: false
```

## Metric Values

```text
M1_NONCOMMUTATOR_SHARE = 1.41421356237
M2_EFFECTIVE_RANK = 0.25
M3_SUPPORT_ENTROPY = 0.333333333333
M4_LABEL_PROXY_OVERLAP = 0
M5_NULL_SEPARATION_MARGIN = 0
M6_OUTCOME_LEAKAGE_CERTIFICATE = true
```

Passing this prescore would only allow a later freeze manifest. It does not
authorize empirical P-TauCov scoring.

## Claim Boundary

Allowed statement:

```text
The epsilon-P candidate has been evaluated by target-blind specificity metrics.
```

Forbidden statement:

```text
The epsilon-P candidate has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
