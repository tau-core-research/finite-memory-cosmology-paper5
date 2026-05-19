# Source-Split Blocker Matrix

Status: blocker matrix updated after candidate export creation; K2 scoring
remains blocked.

This file aggregates the source-split dashboard, handoff manifest, and final
authorization guard into one audit table.

## Run

```text
python3 scripts/build_source_split_blocker_matrix.py
```

It writes:

```text
evidence/source_split_blocker_matrix.csv
evidence/source_split_blocker_matrix_summary.csv
```

## Interpretation

The blocker matrix is not a scoring result. It is the compact operational view
of what must be resolved before source-split K2/null scoring can even be
considered.

The candidate export now exists and validates cleanly:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

The first subtask under that blocker is now the SN branch export handoff:

```text
evidence/source_split_sn_branch_export_handoff.csv
evidence/source_split_sn_branch_export_handoff_summary.csv
```

It shows that `RFAM_SN_RESIDUAL_BRANCH` has eight ready rows, but those rows are
now written to the real candidate export.

The matching BAO branch export handoff is also ready:

```text
evidence/source_split_bao_branch_export_handoff.csv
evidence/source_split_bao_branch_export_handoff_summary.csv
```

It shows that `RFAM_BAO_RESIDUAL_BRANCH` has eight ready rows, but those rows
are also written to the real candidate export.

The matrix should remain K2-blocking until the remaining transform, K1,
covariance, and sign-family gates are resolved and the final authorization
guard returns `AUTHORIZED`.
