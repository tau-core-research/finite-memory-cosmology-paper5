# Source-Split Future K1/K2 Dry Run

Status: future-only dry run completed; current measurement gate remains closed.

This dry run applies the locked K2 operator to the future-only equal-weight
family-mean K1 export. It is not a current measurement scorecard because the
family-mean K1 policy was not frozen before the current source-split scorecard.

## Run

```text
python3 scripts/run_source_split_future_k1_k2_dry_run.py
```

It writes:

```text
evidence/source_split_future_k1_k2_dry_run.csv
evidence/source_split_future_k1_k2_dry_run_summary.csv
```

## Current Result

```text
Rows: 8
CurrentRerunAuthorized: False
FutureOnlyK1Available: True
BestAICModel: POLY_DEG2_CONTROL
K1FamilyMeanAIC: 25.062371419386807
K2Rho4AIC: 52.5499794390236
DeltaAICK2Rho4MinusK1: 27.487608019636795
K2Rho4SignStableViolations: 2
```

## Interpretation

The family-mean route is now informative: when used as a future-only K1
candidate, the locked K2 multiplier worsens the score relative to the K1
family mean itself. This weakens the family-mean path as the next primary
route.

This does not close the finite-memory projection hypothesis. It says that the
secondary family-mean preflight route is not currently promising. The cleaner
next route remains a likelihood-native joint SN+BAO K1/no-memory baseline.
