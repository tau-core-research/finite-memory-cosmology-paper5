# Physical Null Candidate Source Probe

Status: arXiv source packages probed; no calibration values extracted yet.

This probe checks whether the first acquisition targets have source files,
tables, figures, or TeX markers that could support a later provisional
calibration-source CSV.

Outputs:

- `evidence/physical_null_candidate_source_probe.csv`;
- `evidence/physical_null_candidate_source_probe_summary.csv`.

Raw source packages, when downloadable, are stored under
`data/physical_nulls/raw/`.

## Current Reading

The first probe completed for all three acquisition targets:

```text
TargetsProbed: 3
ProbeCompleted: 3
SourcesWithDataLikeFiles: 1
SourcesWithTexTables: 2
SourcesWithFigures: 3
CalibrationInputsReadyNow: 0
RecommendedNextAction: begin provisional extraction from highest-priority completed source probe
PrimaryBlockingIssue: candidate_values_not_extracted_or_mapped
```

The Koksbang backreaction source package exposes a data-like file route. The
two Dyer-Roeder candidates expose TeX/table-marker routes. These routes are
useful for the next extraction step, but none of them is a benchmark input yet.

The follow-up provisional extraction manifest is tracked in
`docs/physical_null_provisional_extraction_manifest.md`. It corrects the
Koksbang route boundary: the apparent data-like file is arXiv package metadata,
so the current backreaction route remains formula/figure/external
reconstruction rather than a source-native numeric table.

## Boundary

The probe does not read values into the benchmark, digitize figures, map source
rows, or propagate covariance. It only records extractability metadata.
