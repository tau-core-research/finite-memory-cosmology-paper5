# P-TauCov Diagonal-Orthogonal Scorecard Interpretation

Audit ID: `P_TAUCOV_DIAGONAL_ORTHOGONAL_ALIGNMENT_SCORECARD_v1`

Status:

`P_TAUCOV_DIAGONAL_ORTHOGONAL_ALIGNMENT_FAIL_NO_SURVIVAL_CLAIM`

## What Improved

The diagonal-orthogonal candidate removed the main diagonal leakage channel by construction and produced a stronger raw signed alignment than the previous branch-localized signed response attempt.

The primary signed statistic is positive:

```text
PrimarySignedS = 59.39929434584365
```

It also exceeds the maximum required null comparator:

```text
RequiredNullMaxSignedS = 48.942922656268905
```

This means the candidate is no longer merely a diagonal-variance or trivial sign-flip effect at the primary-statistic level.

## Why It Still Fails

The candidate does not pass the frozen survival criteria.

The clock aggregate is negative:

```text
ClockSignedS = -3.1122457547899645
```

The positive family contribution is also strongly dominated by one family:

```text
PositiveFamilyCount = 2
MaxPositiveFamilyShare = 0.9883134358570175
```

This violates the frozen family-balance requirement and prevents any survival claim.

## Scientific Interpretation

The result is a constrained positive anomaly, not Tau Core evidence.

It shows that a diagonal-orthogonal, branch-localized signed response can produce a target-aligned statistic stronger than the frozen null maximum. However, the effect is not stable across clock aggregation and is still effectively localized to one dominant family contribution.

Therefore the correct interpretation is:

```text
raw signed alignment improved,
null maximum beaten,
clock consistency failed,
family balance failed,
no survival claim,
no Tau Core validation claim.
```

## Claim Boundary

This scorecard authorizes only the following statement:

> A diagonal-orthogonal branch-localized signed response produced a stronger raw alignment than the frozen null maximum, but failed the frozen clock and family-balance gates.

It does not authorize:

- covariance survival;
- Tau Core validation;
- measurement validation;
- a branch-localized physical response claim;
- promotion of this candidate into a successful P-TauCov test.

## Next Gate

The next admissible route must be designed before scoring and must target the observed failure mode directly:

- clock-consistent support;
- family-balanced support;
- no diagonal leakage;
- no post-score candidate switching;
- no reuse of the failed diagonal-orthogonal score as a tuning objective.

