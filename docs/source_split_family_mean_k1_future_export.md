# Source-Split Family-Mean K1 Future Export

Status: future-only family-mean K1 export created; current K2 rerun remains
closed.

This export materializes the secondary future route from the rerun protocol:
an equal-weight signed mean of the SN and BAO reconstruction-family branch
responses. It is nonzero on all usable source-split rows.

## Run

```text
python3 scripts/build_source_split_family_mean_k1_future_export.py
python3 scripts/validate_source_split_external_k1_export.py
```

It writes:

```text
data/k1/source_split_external_k1_response.csv
evidence/source_split_family_mean_k1_future_export_summary.csv
evidence/source_split_external_k1_export_readiness.csv
```

## Current Result

```text
Rows: 8
NonzeroRows: 8
MeanAbsK1Response: 0.9367627784351423
MeanK1Sigma: 0.7071067811865476
AllowedForCurrentRerun: False
AllowedForFutureRerun: True
AllowedAsPrimaryK1Candidate: False
```

The external K1 validator now reports:

```text
Available: True
AllowedForPrimaryK1: False
BlockingIssue: not_marked_primary_candidate
```

## Interpretation

This is progress, but not a measurement-gate opening. The file gives the next
rerun a concrete K1 candidate, while preserving the current claim boundary:
the family-mean policy was declared after the current scorecard, so it cannot
be used retroactively as primary K1.

The next valid use is a future rerun where this policy is pre-registered before
locked K2 and null-comparator scoring.
