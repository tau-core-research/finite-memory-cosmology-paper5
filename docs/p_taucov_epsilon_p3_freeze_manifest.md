# P-TauCov Epsilon-P3 Freeze Manifest

Status: `FROZEN_SPECIFICITY_CANDIDATE_NO_SCORING`.

This manifest freezes the target-blind epsilon-P3 candidate after the
specificity prescore passed all six structural gates.

## Frozen Candidate

```text
Route: epsilon_P projection response
Operator: P3 core-mixing
lambda_B = 0
epsilon_P = 1
T_tau = A_Phi + A_B L0_B^+ R_B + epsilon_P P3
delta_C_tau = T_tau T_tau^T
```

## Specificity Result

```text
SpecificityPrescoreStatus: PASS_NOT_FROZEN
MetricsPassed: 6/6
TargetResidualsUsed: false
P5CV3OutcomeUsed: false
PTauCovScoringAuthorized: false
```

## Claim Boundary

Allowed statement:

```text
The epsilon-P3 candidate is frozen as a target-blind P-TauCov specificity
candidate.
```

Forbidden statement:

```text
The epsilon-P3 candidate has produced an empirical P-TauCov score, survival
result, or Tau-specific observational signal.
```

The next step may only be a separate scoring-authorization protocol that freezes
folds, nulls, covariance policy, degrees-of-freedom policy, and survival/kill
criteria before any empirical scoring is run.
