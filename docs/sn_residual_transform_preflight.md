# SN Residual Transform Preflight

Status: available as source-split transform-development artifact; not a K2
measurement target.

This preflight uses the local Pantheon+SH0ES distance table and covariance file
to build an audit residual layer:

```text
mu_observed - mu_flat_LCDM_audit
```

with an optional same-sample constant offset subtracted for transform
development. The offset-centered residual is useful for inspecting redshift
structure, but it is not a frozen K1/no-memory target because the offset is
estimated from the same SN sample.

## Outputs

Run:

```text
python3 scripts/build_sn_residual_preflight.py
```

It writes:

```text
evidence/sn_residual_preflight.csv
evidence/sn_residual_binned_preflight.csv
evidence/sn_residual_preflight_summary.csv
```

## Current Interpretation

The full SN table contains 1701 rows. The binned preflight maps the SN residual
rows onto the current diagnostic redshift grid where data are available. This
does not define the final source-split target; it only shows that the public SN
product can be transformed into a controlled residual layer.

The remaining blockers are:

- joint SN+BAO diagnostic reconstruction;
- coordinate-native K1/no-memory target;
- covariance propagation for the joint source-split vector;
- sign-family export from public reconstruction families.

Until those exist, the SN residual output remains preflight evidence only.

