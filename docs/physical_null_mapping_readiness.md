# Physical Null Mapping Readiness

Status: mapping precheck complete; no physical-null benchmark input is
authorized.

This audit checks the provisional physical-null extraction manifest against the
current source-split redshift grid. It asks only whether a candidate source row
has numeric values, uncertainty, redshift coverage, a declared transform to the
source-split response, and covariance propagation.

Outputs:

- `evidence/physical_null_mapping_readiness.csv`;
- `evidence/physical_null_mapping_readiness_summary.csv`.

## Current Reading

The current precheck is expected to remain closed:

- optical Dyer-Roeder rows provide provisional smoothness-parameter values;
- the backreaction candidate remains a route, not a numeric constraint row;
- no row has a declared physical-to-source-split response transform;
- no row has covariance propagation into the benchmark vector.

```text
RowsChecked: 8
RowsWithFullTargetCoverage: 2
RowsWithNumericValue: 7
RowsWithSourceUncertainty: 7
RowsWithTransformToSourceSplit: 0
RowsWithCovariancePropagation: 0
BenchmarkInputsReadyNow: 0
BestCoverageExtractionID: PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR
```

Rows with broad redshift coverage are useful acquisition targets, but they are
not measurement comparators until transform and covariance are attached.

The ranked follow-up queue is tracked in
`docs/physical_null_mapping_task_queue.md`.
The first non-scoring alpha transform preview is tracked in
`docs/physical_null_alpha_transform_contract.md`.

## Boundary

This audit does not fit amplitudes, select a physical null by K2 performance,
or compare physical nulls against the locked prediction. It only records whether
the acquisition rows are technically ready for a future mapping/covariance
stage.
