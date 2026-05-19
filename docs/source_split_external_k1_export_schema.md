# Source-Split External K1 Export Schema

Status: schema and validator added; external K1 export missing.

The source-split K2 comparison now has an explicit contract for the missing
object: an externally derived, nonzero K1/no-memory response target. This is
the object that a locked multiplicative K2 response would multiply.

## Build The Schema

Run:

```text
python3 scripts/build_source_split_external_k1_export_schema.py
```

It writes:

```text
evidence/source_split_external_k1_export_schema.csv
evidence/source_split_external_k1_export_template.csv
```

The template covers the eight usable coordinate-native source-split rows.

## Validate A Candidate

The validator expects a future candidate at:

```text
data/k1/source_split_external_k1_response.csv
```

Run:

```text
python3 scripts/validate_source_split_external_k1_export.py
```

It writes:

```text
evidence/source_split_external_k1_export_readiness.csv
```

Current status:

```text
Available: False
AllowedForPrimaryK1: False
BlockingIssue: external_k1_export_missing
```

## Gate Rule

The export must be:

- row-aligned to the coordinate-native source-split target;
- nonzero on at least part of the usable grid;
- public-input based;
- coordinate-native;
- scored under the same joint covariance policy;
- predeclared before locked K2 scoring;
- not fitted in this note;
- not a same-data amplitude rescue;
- not a single-branch diagnostic control.

Allowed provenance types are:

```text
external_reconstruction_family_mean
likelihood_native_baseline
independent_public_model_response
external_public_response_operator
```

## Interpretation

This schema does not create measurement validation. It prevents a post-hoc K1
rescue by defining what would count as a valid primary K1 before the next
locked K2/null scorecard is run.
