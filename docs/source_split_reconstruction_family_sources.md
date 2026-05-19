# Source-Split Reconstruction-Family Sources

Status: source registry added; no scoring-grade reconstruction-family source is
available.

The branch-sign table is useful, but it is not a public reconstruction-family
response export. This registry separates templates, branch-sign preflights, and
the missing scoring-grade source.

## Outputs

Run:

```text
python3 scripts/check_source_split_reconstruction_family_sources.py
```

It writes:

```text
evidence/source_split_reconstruction_family_source_readiness.csv
```

The registry is:

```text
evidence/source_split_reconstruction_family_source_registry.csv
```

## Current Decision

No source is allowed for K2 scoring.

- `RF_CURRENT_DISTILLED_PACKET` is a method-note template only.
- `RF_PUBLIC_BRANCH_SIGN_PREFLIGHT` is row-aligned and coordinate-native, but
  contains branch signs only.
- `RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES` is required and missing.
- `RF_LIKELIHOOD_NATIVE_RECONSTRUCTION_FAMILIES` remains a later target.

The next real data task is to export public reconstruction-family responses on
the coordinate-native target rows, then declare a family-level sign-stability
rule.

## Export Schema

The required export schema is now frozen by:

```text
python3 scripts/build_source_split_reconstruction_family_export_schema.py
```

It writes:

```text
evidence/source_split_reconstruction_family_export_schema.csv
evidence/source_split_reconstruction_family_export_template.csv
```

The validator is:

```text
python3 scripts/validate_source_split_reconstruction_family_export.py
```

It expects:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

The current validation output is:

```text
evidence/source_split_reconstruction_family_export_validation.csv
```

Current status: `candidate_export_missing`, so K2 scoring remains blocked.

## Candidate Families

The candidate-family plan is:

```text
python3 scripts/build_source_split_reconstruction_family_candidate_plan.py
```

It writes:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

The first practical source candidates are:

- `RFAM_SN_RESIDUAL_BRANCH`;
- `RFAM_BAO_RESIDUAL_BRANCH`.

Both are still marked `PREFLIGHT_AVAILABLE_NOT_FAMILY_EXPORT`. They become
useful only after they are exported into the long-format reconstruction-family
response table and pass validation.

The response-preview builder confirms that the existing SN and BAO branch rows
can be represented in the frozen schema:

```text
evidence/source_split_reconstruction_family_response_preview.csv
evidence/source_split_reconstruction_family_response_preview_summary.csv
```

This preview has `AllowedForK2Scoring = False`.
