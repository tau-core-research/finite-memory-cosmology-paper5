# P-TauCov Diagonal-Orthogonal Failure Diagnostic

Audit ID: `P_TAUCOV_DIAGONAL_ORTHOGONAL_FAILURE_DIAGNOSTIC_v1`

Status:

`P_TAUCOV_CLOCK_AND_FAMILY_FAILURE_LOCALIZED_NO_NEW_SCORING`

## Diagnostic Result

The diagonal-orthogonal scorecard produced a positive raw primary signed statistic and exceeded the frozen null maximum, but the failure is now localized.

```text
PrimarySignedS = 59.39929434584365
RequiredNullMaxSignedS = 48.942922656268905
FamilySignedS = 62.51154010063362
ClockSignedS = -3.1122457547899645
```

## Family Failure

The positive family contribution is concentrated almost entirely in one family:

```text
DominantPositiveFamily = REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY
DominantPositiveFamilySignedS = 63.90761077983775
DominantPositiveFamilyShare = 0.9883134358570175
```

This confirms that the scorecard failure is not merely a weak total signal. The signal is too localized in family space to support a Tau-specific global response claim.

## Clock Failure

The clock aggregation also fails:

```text
ClockPositiveBlockCount = 2
ClockNegativeBlockCount = 1
WorstClockBlock = clock_block_0
WorstClockSignedS = -4.72202405738544
BestClockBlock = clock_block_2
BestClockSignedS = 1.6085048500625865
```

The negative clock aggregate means the candidate does not behave like a stable response across the frozen clock-block partition.

## Family x Clock Localization

The strongest secondary family-by-clock cell is:

```text
BestFamilyClockFold = holdout_REGISTERED_HD_CRITERIA_3_LOSS_COMPLEXITY_clock_block_0
BestFamilyClockSignedS = 12.340959509456312
```

The weakest cell is:

```text
WorstFamilyClockFold = holdout_REGISTERED_HD_CRITERIA_2_LOW_LOSS_PROXY_clock_block_0
WorstFamilyClockSignedS = -2.3885337603702785
```

This supports the same conclusion: the candidate contains a localized alignment feature, but not a globally stable Tau-specific covariance response.

## Claim Boundary

This diagnostic does not authorize a new score, a new candidate, or a survival claim.

It only authorizes the following interpretation:

> The diagonal-orthogonal P-TauCov candidate fails because its positive alignment is clock-inconsistent and family-localized.

## Next Gate

Any next candidate must be defined before scoring and must enforce:

- clock-consistent support;
- family-balanced support;
- zero diagonal leakage;
- no reuse of this failure diagnostic as a post-score tuning objective;
- the same null and claim-boundary discipline as the frozen P-TauCov protocol.
