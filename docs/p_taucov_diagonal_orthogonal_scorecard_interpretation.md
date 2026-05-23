# P-TauCov Diagonal-Orthogonal Scorecard Interpretation

Status: improved signed alignment / fail / no survival claim.

The diagonal-orthogonal signed candidate was designed after the previous signed
scorecard failed through diagonal dominance. That failure mode was removed
before scoring.

## Result

```text
PrimarySignedS = 59.39929434584365
FamilySignedS = 62.51154010063362
ClockSignedS = -3.1122457547899645
RequiredNullMaxSignedS = 48.942922656268905
PositiveFamilyCount = 2
MaxPositiveFamilyShare = 0.9883134358570175
```

## Interpretation

This is a partial improvement over the previous signed-response candidate:

- the diagonal-control failure was removed by construction;
- the primary signed statistic is now above the strongest listed null;
- at least two families contribute positively.

However, the frozen gates still fail:

- the clock aggregate is negative;
- the family contribution remains overwhelmingly dominated by one family.

Therefore this is not a signed-response survivor and not Tau Core validation.

## Scientific Meaning

The diagonal-orthogonal direction is more informative than the previous signed
candidate, but the signal is still not robustly distributed across clock and
family blocks.

The next admissible refinement would need to address clock-consistency and
family-balance at the construction stage, not after observing this result.
