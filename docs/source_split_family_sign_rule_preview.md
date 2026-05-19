# Source-Split Family Sign-Rule Preview

Status: non-scoring sign-rule preview added.

The response preview shows that the SN and BAO residual branches can be
represented in the frozen reconstruction-family schema. This note adds the
row-level family-sign rule preview on top of that export.

## Build The Preview

Run:

```text
python3 scripts/build_source_split_family_sign_rule_preview.py
```

It writes:

```text
evidence/source_split_family_sign_rule_preview.csv
evidence/source_split_family_sign_rule_preview_summary.csv
```

## Preview Rule

The preview rule is:

```text
stable if all nonzero public reconstruction-family signs agree
```

Rows that do not satisfy this rule remain warnings. They are not hidden support
and not hidden rejection.

## Boundary

This is not the scoring rule yet. It can only be promoted after a real candidate
export exists at:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

and that export passes validation.

## Promotion Readiness

Run:

```text
python3 scripts/check_source_split_sign_rule_promotion.py
```

It writes:

```text
evidence/source_split_sign_rule_promotion_readiness.csv
```

Current status:

```text
rule_promotion_authorized = false
candidate_export_missing
```
