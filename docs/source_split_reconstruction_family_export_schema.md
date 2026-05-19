# Source-Split Reconstruction-Family Export Schema

Status: schema and validator added; candidate export missing.

The source-split branch now has a precise input contract for the missing public
reconstruction-family responses. This is still a pre-scoring artifact. It does
not authorize K2 scoring and does not add a measurement-validation claim.

## Build The Schema

Run:

```text
python3 scripts/build_source_split_reconstruction_family_export_schema.py
```

It writes:

```text
evidence/source_split_reconstruction_family_export_schema.csv
evidence/source_split_reconstruction_family_export_template.csv
```

The export must be long-format: one row per reconstruction family per
coordinate-native target row. At least two public reconstruction families are
required, and every family must cover every usable target row.

## Validate A Candidate Export

The validator expects a future candidate at:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

Run:

```text
python3 scripts/validate_source_split_reconstruction_family_export.py
```

It writes:

```text
evidence/source_split_reconstruction_family_export_validation.csv
```

Current expected status:

```text
candidate_export_missing
AllowedForK2Scoring = False
```

## Minimum Gate Rule

K2 scoring may only be considered after the candidate export passes these
checks:

- at least two reconstruction families;
- row alignment to the coordinate-native source-split target;
- finite response values;
- positive response sigmas;
- valid response signs;
- coordinate-native flag true;
- not fitted inside this note.

Until then, the public branch-sign preflight remains a warning control only.

## Candidate Plan

The first candidate-family plan is:

```text
python3 scripts/build_source_split_reconstruction_family_candidate_plan.py
```

It writes:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

The primary practical candidates are the Pantheon+ SN residual branch and the
DESI DR2 BAO residual branch. They are public-input candidates, but they still
need to be exported into the schema above before any scorecard can run.

The non-scoring schema preview is:

```text
python3 scripts/build_source_split_reconstruction_family_response_preview.py
```

It writes:

```text
evidence/source_split_reconstruction_family_response_preview.csv
evidence/source_split_reconstruction_family_response_preview_summary.csv
```

The current preview is schema-valid and contains two families across the eight
usable target rows. It is still not a scoring input.
