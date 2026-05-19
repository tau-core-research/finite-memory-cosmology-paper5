# Physical Null Row Audit

Status: row-level preflight diagnosis; no measurement validation claim.

This audit decomposes the physical-null preflight scorecard row by row. Its
purpose is to check whether the aggregate K2 advantage is broad across the
source-split vector or concentrated in only a few rows.

Outputs:

- `evidence/physical_null_preflight_row_audit.csv`;
- `evidence/physical_null_preflight_row_summary.csv`.

## What It Compares

For each usable source-split row, the audit compares:

- K1/no-memory contribution;
- locked K2 contribution;
- the best reported physical-null template contribution for diagnostics only.

The phrase "best reported physical-null template" is bookkeeping, not an
amplitude selection for interpretation. Every allowed amplitude remains
reported in the full scorecard.

## Boundary

The audit does not modify K2, does not fit K1, does not allow `rho>4`, and does
not calibrate physical-null amplitudes. It can strengthen or weaken the
preflight reading, but it cannot produce measurement validation.

## Current Reading

The current row summary reports:

```text
RowsWhereK2BeatsK1: 8
RowsWhereK2BeatsBestPhysicalNull: 4
RowsWhereBestPhysicalNullBeatsK2: 4
RowsWhereK2HasSignViolation: 0
RowsWhereBestPhysicalHasSignViolation: 0
NetDeltaChi2_K2_minus_K1: -3.7513845266078616
NetDeltaChi2_K2_minus_BestPhysical: -0.3601026940036727
```

This is supportive but narrow at preflight level. K2 improves over K1/no-memory
on every row, and it has no sign-stable contradiction. Against the best reported
physical-null template row by row, the result is split 4-4, with a small net K2
advantage. The physical-null layer therefore remains competitive enough that
independent amplitude calibration is still required before stronger
interpretation.

The required calibration routes are registered in
`docs/physical_null_calibration_requirements.md`.
The candidate source classes are registered in
`docs/physical_null_calibration_source_registry.md`.
