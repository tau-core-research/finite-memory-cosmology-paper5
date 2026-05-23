# P-TauCov Signed-Response Scorecard Interpretation

Status: signed alignment fail / no survival claim / no Tau Core validation.

The signed-response scorecard was authorized only for the narrow signed
alignment scope. It was not a covariance-likelihood scorecard and it did not
authorize survival language.

## Result

```text
PrimarySignedS = 31.70572026946584
FamilySignedS  = 30.03171856933994
ClockSignedS   = 1.6740017001259013
RequiredNullMaxSignedS = 152.41444638165376
MaxPositiveFamilyShare = 0.998171886220409
```

The signed statistic is positive, but it fails the frozen signed protocol:

1. the diagonal signed control is much larger than the candidate;
2. the positive family contribution is almost entirely single-family dominated.

## Interpretation

This is not a Tau Core validation signal.

It is also not a clean branch-localized signed-response survivor. The result
looks more like a diagonal/family-dominated alignment than a robust
projection-specific signed operator response.

## Consequence

The signed route should not be promoted to a positive result. The correct
status is:

```text
P_TAUCOV_SIGNED_RESPONSE_ALIGNMENT_FAIL_NO_SURVIVAL_CLAIM
```

The next admissible route would need to eliminate diagonal dominance and
single-family dominance before scoring, not after observing this failure.
