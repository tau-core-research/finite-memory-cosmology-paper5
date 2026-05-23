# P-TauCov P3 Balanced Scoring Policy Freeze

Freeze ID: `P_TAUCOV_P3_BALANCED_SCORING_POLICY_FREEZE_v1`

Status:

`P_TAUCOV_P3_BALANCED_SCORING_POLICY_FROZEN_NO_SCORING`

## Scope

This freezes the policy that would govern any later P3 balanced signed-alignment scorecard.

It does not authorize scoring.

## Primary Statistic

```text
trace((rrT/sigma2-I)K_p3_balanced)
```

## Required Gates

- primary OOS signed statistic must be positive;
- primary OOS signed statistic must beat the required null maximum;
- family aggregate must be positive;
- clock aggregate must be positive;
- at least two families must contribute positively;
- maximum positive-family share must be at most 0.5.

## Claim Boundary

Allowed statement:

> A scoring policy has been frozen for the P3 balanced object.

Forbidden statement:

> The P3 balanced object is authorized for scoring, has survived scoring, or validates Tau Core.
