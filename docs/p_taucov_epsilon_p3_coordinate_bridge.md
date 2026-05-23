# P-TauCov Epsilon-P3 Coordinate Bridge

Status: `FROZEN_COORDINATE_BRIDGE_NO_SCORING`.

This artifact freezes a target-blind bridge from the 8-dimensional P-TauCov
Tau-coordinate basis to the 36-row empirical family-clock grid used by the
P5C covariance scorecard family.

The bridge uses only metadata and frozen P5C v3 manifest conventions:

```text
PHI_PARENT_SOURCE      -> constant source feature
B_BRANCH_RESPONSE     -> frozen branch-sign feature
M_PARENT_MORPHOLOGY   -> frozen clock-sector weight
P_MORPH_PROJECTION    -> branch-sign * sector-weight * cos(clock phase)
other coordinates     -> zero
```

It does not use target residuals, P5C v3 gain patterns, OOS DeltaNLL values, or
family-localized outcome information.

## Metrics

```text
EmpiricalRows: 36
TauCoordinates: 8
ActiveBridgeColumns: 4
BridgeRank: 4
MaxAbsActiveColumnCorrelation: 0.0286436890793
PTauCovScoringAuthorized: false
```

Allowed statement:

```text
A target-blind coordinate bridge has been frozen for epsilon-P3 P-TauCov.
```

Forbidden statement:

```text
The bridge has produced an empirical Tau signal or authorizes scoring by
itself.
```
