# Source-Split Joint Preflight

Status: available as transform-development artifact; not a measurement gate.

This artifact aligns three existing layers on the current diagnostic redshift
grid:

- the distilled SN+BAO sign-stability packet;
- binned Pantheon+ SN residual preflight rows;
- nearest DESI DR2 BAO residual anchor rows.

The output is intentionally not a K2 score. SN distance-modulus residuals and
BAO log-distance residuals are not yet on a common source-split response scale,
and the joint covariance has not been exported.

## Outputs

Run:

```text
python3 scripts/build_source_split_joint_preflight.py
```

It writes:

```text
evidence/source_split_joint_preflight.csv
evidence/source_split_joint_preflight_summary.csv
```

## Current Interpretation

The current preflight has nine diagnostic-grid rows. Eight rows have both an
SN bin and a BAO anchor. The missing piece is not raw data availability; it is
the shared diagnostic definition:

- common residual units or response scale;
- coordinate-native K1/no-memory target;
- joint covariance propagation;
- sign-family export from public reconstruction families.

Until those exist, the joint table is useful for transform design only.

