# Physical Null Public Source Candidates

Status: public source candidates registered; no candidate is ingested, mapped,
or covariance-ready.

This inventory lists concrete public-paper candidates for future physical-null
amplitude calibration. It is not a data ingestion result and it does not promote
any physical null to measurement status.

Outputs:

- `evidence/physical_null_public_source_candidates.csv`;
- `evidence/physical_null_public_source_candidate_readiness.csv`.

## Candidate Classes

The candidate list includes:

- recent backreaction constraint papers;
- the Heinesen-Clifton optical-vs-expansion consistency-test framework;
- Dyer-Roeder / ZKDR smoothness-parameter constraints from SNe and GRBs;
- weak-lensing to Dyer-Roeder smoothness mapping references.

## Current Reading

The current state is acquisition-only:

```text
PhysicalNullSourceCandidateReady: false
PrimaryBlockingIssue: candidate_sources_not_ingested_digitized_or_mapped
```

The next work is to inspect the candidate papers for tables, source files, or
extractable constraints, then export row-aligned source CSVs with uncertainties.

The acquisition triage is tracked in `docs/physical_null_candidate_triage.md`.
The source-package extractability probe is tracked in
`docs/physical_null_candidate_source_probe.md`.
The provisional extraction manifest is tracked in
`docs/physical_null_provisional_extraction_manifest.md`.
