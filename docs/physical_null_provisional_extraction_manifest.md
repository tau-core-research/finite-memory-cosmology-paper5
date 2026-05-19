# Physical Null Provisional Extraction Manifest

Status: provisional source values/routes recorded; no benchmark input is
authorized.

This manifest is the next acquisition layer after the source-package probe. It
records candidate physical-null quantities that are visible in public arXiv
source packages while keeping them blocked until mapping and covariance are
declared.

Outputs:

- `evidence/physical_null_provisional_extraction_manifest.csv`;
- `evidence/physical_null_provisional_extraction_summary.csv`.

## Current Reading

```text
RowsExtracted: 8
BackreactionRows: 1
DyerRoederRows: 7
BenchmarkInputsReadyNow: 0
RowsBlockedForBenchmark: 8
PrimaryBlockingIssue: mapping_and_covariance_missing
```

The manifest separates three cases:

- Koksbang backreaction: formula/figure route identified, but no source-native
  numeric constraint table is extracted from the source package.
- Breton-Montiel Dyer-Roeder: TeX-table smoothness-parameter constraints are
  recorded as provisional optical-null candidates.
- Yang-Yu-Zhang Dyer-Roeder / distance-duality: TeX-text smoothness and
  distance-duality constraints are recorded as provisional optical controls.

None of these rows is a measurement-gate input yet. The next required step is a
declared mapping to the source-split vector plus source-native uncertainty or
covariance propagation.

The mapping-readiness precheck is tracked in
`docs/physical_null_mapping_readiness.md`.

## Boundary

This artifact does not fit amplitudes, select rows by K2 performance, alter the
locked K2 kernel, or validate the finite-memory projection hypothesis. It only
creates a controlled acquisition manifest for future public physical-null
calibration work.
