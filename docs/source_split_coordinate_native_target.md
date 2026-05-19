# Source-Split Coordinate-Native Target

Status: preflight target exported; not a K1 target and not K2 scoring.

This artifact completes the first source-split export task:

```text
TQ1_COORDINATE_NATIVE_TRANSFORM
```

It maps the standardized SN-minus-BAO branch contrast onto a declared audit
coordinate:

```text
x = chi(z) / chi(z_max)
```

using a flat-LCDM audit mapping. The response column is:

```text
SourceSplitResponse = SN_standardized - BAO_standardized
```

This response is a target-vector preflight. It does not define the no-memory
baseline and it does not authorize K2 scoring.

## Outputs

Run:

```text
python3 scripts/build_source_split_coordinate_native_target.py
```

It writes:

```text
evidence/source_split_coordinate_native_target.csv
evidence/source_split_coordinate_native_target_summary.csv
```

## Current Interpretation

The exported target has nine grid rows, with eight usable rows containing both
SN and BAO branches. It keeps the source-split warning visible while moving the
branch into a declared coordinate-native preflight space.

The remaining blockers are:

- coordinate-native K1/no-memory target;
- joint covariance;
- public sign-family export.

