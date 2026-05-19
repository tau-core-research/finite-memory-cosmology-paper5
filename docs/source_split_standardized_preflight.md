# Source-Split Standardized Preflight

Status: common audit scale available; not a measurement gate.

The joint SN+BAO preflight exposed a unit mismatch: SN residuals are in
distance-modulus units, while BAO residuals are log-distance-ratio residuals.
This preflight maps both branches to dimensionless residual coordinates by
dividing each branch residual by its diagonal uncertainty:

```text
SN_standardized  = SN_centered_residual / sigma_SN
BAO_standardized = BAO_log_residual / sigma_BAO
```

This is a shared audit scale, not a final physical response variable. It does
not export a K1/no-memory target and it does not authorize K2 scoring.

## Outputs

Run:

```text
python3 scripts/build_source_split_standardized_preflight.py
```

It writes:

```text
evidence/source_split_standardized_preflight.csv
evidence/source_split_standardized_preflight_summary.csv
evidence/source_split_sign_tension_audit.csv
evidence/source_split_sign_tension_summary.csv
evidence/source_split_covariance_sensitivity.csv
evidence/source_split_covariance_sensitivity_summary.csv
```

## Current Interpretation

The standardized preflight keeps eight rows with both SN and BAO branches. Five
of those rows have opposite SN/BAO standardized signs. This is a useful
source-split warning: the public branches are not yet collapsing into a single
clean response target.

The sign-tension diagnosis makes the warning sharper: among rows that are
sign-stable in the current distilled packet and have both SN and BAO branches,
four of five have opposite standardized SN/BAO signs. This is not a K2 result,
because the table still uses diagonal standardization and no coordinate-native
K1 target. It is, however, a strong reason to treat source splitting as a real
next object of study rather than a cosmetic aggregation step.

The result should not be interpreted as support for or rejection of K2. It says
only that the next source-split target must define a joint covariance and a
coordinate-native K1/no-memory response before the finite-memory multiplier can
be evaluated.

## Covariance Sensitivity

Run:

```text
python3 scripts/run_source_split_covariance_sensitivity.py
```

This stress test applies simple within-row SN-BAO correlation proxies from
negative to positive correlation. It does not replace a public joint covariance.

Current result:

- the opposite-sign row count remains five of eight across the tested proxy
  correlations;
- sign-stable opposite-sign rows remain four of five;
- the mean standardized contrast changes with the assumed correlation, as
  expected.

This strengthens the interpretation that the source-split warning is not just
a formatting artifact of the uncorrelated diagonal table. It still does not
authorize K2 scoring.
