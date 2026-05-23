# P-TauCov Epsilon-P3 Specificity Prescore

Status: evaluated / epsilon-P3 candidate not yet frozen / P-TauCov scoring not
authorized.

This prescore evaluates the target-blind epsilon-P3 model packet:

```text
T_tau_epsilon = A_Phi + A_B L0_B^+ R_B + epsilon_P P3
delta_C_tau = T_tau_epsilon T_tau_epsilon^T
```

The strict-linear base term cancels, so the active nonzero structure comes from
the frozen `P3` projection-response operator.

## Result

```text
Status: PASS_NOT_FROZEN
MetricsPassed: 6/6
||T_tau_epsilon||_F = 1
PTauCovScoringAuthorized: false
```

## Metric Values

```text
M1_NONCOMMUTATOR_SHARE = 0.816496580928
M2_EFFECTIVE_RANK = 0.288675134595
M3_SUPPORT_ENTROPY = 0.40250624988
M4_LABEL_PROXY_OVERLAP = 0
M5_NULL_SEPARATION_MARGIN = 0.288675134595
M6_OUTCOME_LEAKAGE_CERTIFICATE = true
```

Passing this prescore would only allow a later freeze manifest. It does not
authorize empirical P-TauCov scoring.

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 candidate has been evaluated by target-blind specificity metrics.
```

Forbidden statement:

```text
The epsilon-P3 candidate has produced a P-TauCov score, survival result, or
empirical Tau signal.
```
