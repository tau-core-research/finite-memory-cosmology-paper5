# Physical Null Mapping Task Queue

Status: next mapping tasks ranked; no benchmark gate is open.

This queue ranks provisional physical-null extraction rows by source-split
coverage and basic source uncertainty availability. It does not select a row by
K2 performance and does not turn any physical null into a measurement
comparator.

Outputs:

- `evidence/physical_null_mapping_task_queue.csv`;
- `evidence/physical_null_mapping_task_queue_summary.csv`.

## Current Reading

The first mapping candidates are the joint Dyer-Roeder smoothness-parameter
rows because they cover the full current source-split redshift grid. They still
need an independently declared `alpha -> source-split response` transform and
uncertainty propagation before any scorecard use.

```text
RecommendedFirstTask: PNMAP_01
RecommendedFirstExtractionID: PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR
BenchmarkGateOpenTasks: 0
PrimaryBlockingIssue: transform_and_covariance_missing
```

The Koksbang backreaction route remains scientifically important, but it is not
first in the mapping queue because a numeric backreaction envelope or
reconstruction table has not yet been extracted.

The first transform contract for the optical queue is tracked in
`docs/physical_null_alpha_transform_contract.md`.

## Boundary

This queue is an operational acquisition aid only. It does not change the locked
K2 operator, does not fit a physical-null amplitude, and does not validate the
finite-memory projection hypothesis.
