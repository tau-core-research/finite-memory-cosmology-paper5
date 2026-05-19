# Source-Split Reconstruction-Family Candidate Export

Status: candidate export created and schema validation is clean.

This artifact combines the SN and BAO branch handoff rows into the real
long-format reconstruction-family candidate export:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

## Run

```text
python3 scripts/build_source_split_reconstruction_family_candidate_export.py
python3 scripts/validate_source_split_reconstruction_family_export.py
```

The export contains:

```text
families: 2
usable target rows per family: 8
total data rows: 16
family ids: RFAM_SN_RESIDUAL_BRANCH, RFAM_BAO_RESIDUAL_BRANCH
```

## Gate Result

The validation output is:

```text
evidence/source_split_reconstruction_family_export_validation.csv
```

Current validation status:

```text
Available: True
AllowedForK2Scoring: True
FamilyCount: 2
UsableTargetRows: 8
BlockingIssue: empty
```

## Boundary

This export is benchmark input plumbing. It does not by itself run K2, validate
the finite-memory projection hypothesis, or produce a measurement result.

K2 scoring remains blocked by the final authorization guard until the remaining
transform, K1, covariance, and sign-family gates are resolved.
