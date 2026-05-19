# Physical Null Candidate Triage

Status: acquisition triage complete; no candidate is a measurement input yet.

This triage ranks the public-paper candidates for physical-null calibration
source acquisition. It distinguishes likely direct amplitude/constraint sources
from method references.

Outputs:

- `evidence/physical_null_candidate_triage.csv`;
- `evidence/physical_null_candidate_triage_summary.csv`.

## Current Reading

The first acquisition targets are:

1. Koksbang 2026 backreaction constraints;
2. Breton-Montiel 2013 Dyer-Roeder / ZKDR smoothness constraints;
3. Yang-Yu-Zhang 2013 Dyer-Roeder smoothness and distance-duality constraints.

The Heinesen-Clifton paper and the weak-lensing/Dyer-Roeder references remain
important method references, but they are not first-pass amplitude sources.

The first source-package probe has now been completed and is tracked in
`docs/physical_null_candidate_source_probe.md`. It finds extractability routes
for all three first acquisition targets, while keeping calibration input status
closed until values, mappings, and covariance are exported.

The provisional extraction manifest is tracked in
`docs/physical_null_provisional_extraction_manifest.md`. It records optical
smoothness-parameter candidates from the Dyer-Roeder sources and keeps the
Koksbang backreaction branch at route-only status.

## Boundary

This artifact does not digitize figures, extract tables, map sources to the
source-split vector, or propagate covariance. It only prioritizes the next data
acquisition work.
