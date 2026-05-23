# P-TauCov Epsilon-P3 Observed Input Contract

Status: `BRIDGE_READY_CONTRACT_NO_SCORING`.

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
ShapeCompatibility: true
```

The P3 branch support is defined in Tau-coordinate space. Empirical scoring
requires the frozen target-blind coordinate bridge before the scorecard can
project the Tau-side response into family-clock space.

Forbidden statement:

```text
The observed input contract authorizes P-TauCov scoring.
```
