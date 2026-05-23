# P5C Kernel v3 Scoring Mode Freeze

Status: `SCORING_MODE_FREEZE_READY`

This freeze chooses the scoring-mode direction using target-blind structural retention metrics only.
It does not authorize scoring.

## Decision

- primary scoring mode: `PSD_COVARIANCE_DEFORMATION`
- secondary mode: `SIGNED_OPERATOR_CONTRAST_DIAGNOSTIC_ONLY`
- scoring authorized by this artifact: `false`

## Metrics

- PSD orientation retention: 0.94442294749796
- PSD random smooth median abs correlation: 0.15610567297012026
- PSD random smooth max abs correlation: 0.21839832875200532
- PSD diagonal energy share: 0.09951979544422788
- PSD max family block energy share: 0.11592314230930299
- PSD max family gain capacity: 0.14409624547883987
- PSD wrong-clock abs correlation: 0.003942300947535861
- PSD phase-shift abs correlation: 0.07912704720635289
- PSD family-permuted abs correlation: 0.12167379515717487

## Boundary

The signed orientation score may be reported only as a diagnostic under this freeze.
It cannot become a survival claim if the PSD primary score fails.
