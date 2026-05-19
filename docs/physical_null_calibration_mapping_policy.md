# Physical Null Calibration Mapping Policy

Status: mapping policy registered; no physical-null source is mapped yet.

This policy defines how a future backreaction or optical calibration source may
be projected onto the same source-split coordinate vector used by the preflight
K2 benchmark.

Outputs:

- `evidence/physical_null_calibration_mapping_policy.csv`;
- `evidence/physical_null_calibration_mapping_readiness.csv`.

## Mapping Rule

Future physical-null calibration sources must be mapped to
`SS_TARGET_COORDINATE_NATIVE_V1`. The allowed operation is monotone
interpolation in source redshift or in a declared source coordinate, followed by
row alignment to the target `GridIndex` values.

Extrapolation is not allowed. Smoothing is allowed only if it comes from the
source product itself; it must not be selected from K2 residuals.

## Normalization Rule

For measurement-level use, the externally calibrated amplitude must be
preserved. Unit-norm normalization remains allowed only for preflight template
controls.

## Current Reading

The policy is frozen, but no source table has been ingested or mapped:

```text
PhysicalNullMappingReady: false
PrimaryBlockingIssue: source_data_not_ingested;mapping_not_executed
```

Thus the next step is source ingestion, not K2 modification.

The corresponding covariance policy is registered in
`docs/physical_null_calibration_covariance_policy.md`.
