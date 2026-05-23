# P-TauCov Epsilon-P3 Observed Input Contract

Status: `BLOCKED_COORDINATE_SPACE_MISMATCH`.

This contract defines the observed input required by the frozen epsilon-P3
scorecard.

The required scorecard input is a long-form matrix:

```text
RowCoordinate
ColumnCoordinate
ObservedWhitenedCovarianceResidual
```

The coordinate IDs must match the frozen P-TauCov Tau-coordinate support.

## Current Blocker

```text
RequiredDimension: 8
AvailableP5Cv3ScorecardRows: 17
ShapeCompatibility: false
```

The current P3 branch support is defined in Tau-coordinate space. The available
P5C empirical covariance artifacts are in family-clock scorecard space. A
target-blind bridge from Tau-coordinate space to empirical family-clock space
must be frozen before empirical scoring can be authorized.

Forbidden statement:

```text
The observed input contract authorizes P-TauCov scoring.
```
