# Physical Null Calibration Requirements

Status: calibration requirements registered; no calibrated physical-null
amplitude is available yet.

The physical-null preflight scorecard shows that backreaction-only and
Dyer-Roeder/optical controls are competitive enough to remain active blockers.
This document defines what would be required before those controls could become
measurement-grade comparators.

Outputs:

- `evidence/physical_null_calibration_requirements.csv`;
- `evidence/physical_null_calibration_readiness.csv`.

## Required Calibration Routes

Backreaction-only control requires a public backreaction reconstruction,
envelope, or independent simulation-prior amplitude on the same source-split
coordinate vector.

Dyer-Roeder/optical control requires a public optical clumpiness, opacity,
lensing, or Dyer-Roeder `alpha(z)` constraint mapped to the same vector.

Both routes require covariance information and must be frozen before any locked
K2 scorecard inspection.

## Forbidden Route

The same scorecard residuals must not be used to choose a physical-null
amplitude. Least-squares, AIC, BIC, or row-wise residual inspection on the
tested vector would be a post-hoc amplitude rescue, not a physical-null
calibration.

## Current Reading

The current readiness status is:

```text
PhysicalNullMeasurementReady: false
PrimaryBlockingIssue: physical_null_calibration_inputs_missing
```

Thus the physical-null layer is useful for preflight sanity and sensitivity
checks, but it is not yet a measurement-level alternative to K2.

The candidate source classes and task queue are registered in
`docs/physical_null_calibration_source_registry.md`.
The row-alignment policy is registered in
`docs/physical_null_calibration_mapping_policy.md`.
The uncertainty policy is registered in
`docs/physical_null_calibration_covariance_policy.md`.
