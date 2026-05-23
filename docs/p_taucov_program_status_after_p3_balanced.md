# P-TauCov Program Status After P3 Balanced Scorecard

Status:

`P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_P3_BALANCED_NEGATIVE_NO_TAU_SIGNAL`

## Executed Route Ladder

The P-TauCov program has now executed a stricter route ladder:

| Route | Primary result | Status |
|---|---:|---|
| Parent-action PSD covariance | `-0.2996400323571766` | fail |
| Initial signed response | `31.70572026946584` | fail versus required null / family dominated |
| Diagonal-orthogonal signed response | `59.39929434584365` | beats null max, but fails clock/family gates |
| P3 balanced signed response | `-11.356021597674012` | negative primary alignment |

## Scientific Interpretation

This is a strong negative-control result.

The earlier local positive anomaly did not survive the stricter path:

1. diagonal leakage was removed;
2. family/clock balance was imposed;
3. structural nulls were audited;
4. a frozen P3 balanced scorecard was authorized and run.

The result was negative:

```text
P3BalancedPrimaryS = -11.356021597674012
P3BalancedFamilyS = -13.44609839972094
P3BalancedClockS = 2.090076802046928
StrongestNullID = SIGN_FLIP_ORIENTATION_CONTROL
```

## Claim Boundary

Allowed statement:

> The current P-TauCov implementation is reproducible and methodologically disciplined, but the tested parent-action, signed, diagonal-orthogonal, and P3 balanced candidates do not provide a surviving Tau-specific empirical signal.

Forbidden statement:

> P-TauCov validates Tau Core, establishes a physical covariance response, or provides a survival claim.

## Next Admissible Direction

The next route should not be a v4 support tweak.

Any future Tau-specific attempt needs a genuinely new parent-derived response structure, for example:

- a different parent Hessian channel;
- an independently motivated external observable family;
- a new source of phase/orientation structure not derived from the failed scorecards;
- or a decision to close P-TauCov as negative for this dataset and move to a different empirical domain.
