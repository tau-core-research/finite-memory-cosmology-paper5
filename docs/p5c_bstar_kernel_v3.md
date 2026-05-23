# P5C Bstar Kernel v3

Status: `FREEZE_READY`

v3 is a residual-complex orientation pre-score artifact.
It stores a signed orientation kernel separately from its PSD covariance projection.
This document does not authorize scoring.

## Diagnostics

- rows: 36
- families: 3
- clock positions: 12
- wrong-clock abs correlation: 0.02249056431761108
- phase-shift abs correlation: 0.003825691677168082
- family-permuted abs correlation: 0.02684840828204191
- random smooth PSD median abs correlation: 0.09968723078954764
- random smooth PSD max abs correlation: 0.14085004891734365
- diagonal energy share: 0.0
- max family block energy share: 0.09026789783864407
- max family gain capacity: 0.10038689199042053
- PSD positive spectral energy retained: 0.8879652733734626
- signed orientation sha256: `1a242c2d677d042dbd7722f3e1542712c96c357975daac970c094b564d27a1a4`
- PSD projection sha256: `5c96dd9ceb6a758d990ddeccdbd4b53a797d1531f527af36f895379c40ec7ad7`

## Scoring Boundary

`SCORING_AUTHORIZED=false`.

If the pre-score gate fails, this candidate is not scoreable and must not be used
as a post-hoc replacement for v2.

## Scoring-Mode Freeze

The scoring-mode freeze selected:

```text
primary_scoring_mode = PSD_COVARIANCE_DEFORMATION
secondary_mode = SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY
```

The signed orientation kernel remains the theoretical source artifact. The PSD
projection is the only primary scoreable covariance artifact under the current
P5C protocol. Signed contrast is diagnostic-only unless a separate signed
operator-contrast protocol is opened and frozen.
