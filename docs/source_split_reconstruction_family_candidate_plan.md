# Source-Split Reconstruction-Family Candidate Plan

Status: candidate plan added; no candidate is allowed for K2 scoring yet.

The missing source-split object is a public reconstruction-family response
export. This plan lists the first candidate families that could populate that
export without changing the locked K2 kernel or fitting a new K1 inside this
note.

## Build The Plan

Run:

```text
python3 scripts/build_source_split_reconstruction_family_candidate_plan.py
```

It writes:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

## Candidate Families

The first two practical candidates are:

- `RFAM_SN_RESIDUAL_BRANCH`: Pantheon+ binned SN residual branch;
- `RFAM_BAO_RESIDUAL_BRANCH`: DESI DR2 BAO residual branch.

They are public-input candidates, but they are not yet exported in the required
long-format reconstruction-family schema.

Two later fair-null controls are registered as missing sources:

- `RFAM_BACKREACTION_ENVELOPE_CONTROL`;
- `RFAM_DYER_ROEDER_OPTICAL_CONTROL`.

## Current Decision

No candidate is allowed for K2 scoring. The next useful work is to export the
SN and BAO residual branches into:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

using the template:

```text
evidence/source_split_reconstruction_family_export_template.csv
```

The export must then pass:

```text
python3 scripts/validate_source_split_reconstruction_family_export.py
```

## Non-Scoring Preview

A schema preview can be built from the existing SN and BAO branch preflight
rows:

```text
python3 scripts/build_source_split_reconstruction_family_response_preview.py
```

It writes:

```text
evidence/source_split_reconstruction_family_response_preview.csv
evidence/source_split_reconstruction_family_response_preview_summary.csv
```

This preview is useful for checking the long-format schema. It remains blocked
for K2 scoring because it is not the candidate export, the family-level rule is
not locked, and the covariance policy is not promoted to the scoring benchmark.
