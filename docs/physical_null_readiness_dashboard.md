# Physical Null Readiness Dashboard

Status: dashboard registered; physical-null measurement validation remains
blocked.

This dashboard aggregates the physical-null hierarchy, amplitude policy,
preflight scorecard, row audit, source registry, mapping policy, and covariance
policy into one machine-readable status.

Outputs:

- `evidence/physical_null_readiness_dashboard.csv`;
- `evidence/physical_null_readiness_summary.csv`.

## Current Reading

The physical-null branch has useful preflight evidence: K2 improves over
K1/no-memory and has a small aggregate advantage over the reported
physical-null sanity/sensitivity controls. The row audit is narrower: K2 beats
the best reported physical-null row on four of eight rows.

Measurement validation remains blocked because:

- no physical-null calibration source is ingested;
- no source is mapped to the source-split target rows;
- no source covariance is propagated.

## Boundary

The dashboard does not modify K2, fit K1, select a physical-null amplitude, or
promote any source route. It is a readiness view only.

The public-paper candidate inventory is tracked in
`docs/physical_null_public_source_candidates.md`.
The candidate acquisition order is tracked in
`docs/physical_null_candidate_triage.md`.
