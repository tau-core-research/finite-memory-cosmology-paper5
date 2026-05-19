# Physical Null Calibration Source Registry

Status: source classes registered; no calibration source is ingested or mapped
yet.

This registry turns the physical-null calibration blocker into concrete source
tasks. It does not calibrate amplitudes and does not promote the physical-null
templates to measurement-grade comparators.

Outputs:

- `evidence/physical_null_calibration_source_registry.csv`;
- `evidence/physical_null_calibration_source_readiness.csv`;
- `evidence/physical_null_calibration_task_queue.csv`.

## Candidate Source Classes

The registered candidate classes are:

- public backreaction constraints or envelopes over redshift;
- independent simulation priors for backreaction amplitude;
- public Dyer-Roeder `alpha(z)` / optical clumpiness constraints;
- lensing, opacity, or foreground-visibility proxies for optical propagation.

All candidate sources must be mapped to the same source-split coordinate vector
and must carry covariance or uncertainty information before any stronger
comparison.

## Forbidden Source

The same scorecard residuals cannot be used to choose a physical-null amplitude.
That route is registered only as a forbidden path.

## Current Reading

The current readiness state is:

```text
PhysicalNullCalibrationSourceReady: false
PrimaryBlockingIssue: candidate_sources_registered_but_not_ingested_or_mapped
```

The next work is data/source acquisition, not K2 modification.

The mapping policy for any future source is registered in
`docs/physical_null_calibration_mapping_policy.md`.
The covariance policy for any future source is registered in
`docs/physical_null_calibration_covariance_policy.md`.
Concrete public-paper candidates are listed in
`docs/physical_null_public_source_candidates.md`.
