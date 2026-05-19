# Source-Split Reconstruction-Family Response Preview

Status: schema preview added; K2 scoring remains blocked.

The response preview converts the existing SN and BAO standardized residual
branches into the frozen reconstruction-family schema. It is intentionally
written to `evidence/`, not to the scoring candidate path under `data/`.

## Build The Preview

Run:

```text
python3 scripts/build_source_split_reconstruction_family_response_preview.py
```

It writes:

```text
evidence/source_split_reconstruction_family_response_preview.csv
evidence/source_split_reconstruction_family_response_preview_summary.csv
```

## Interpretation

The preview answers only one question: can the existing SN and BAO branch
preflight rows be represented in the required long-format schema?

It does not answer whether K2 is supported by the data. It does not open the
K2/null scorecard.

The preview remains blocked as a scoring input because:

- it is not written to the candidate path;
- the family-level sign rule is not locked as a scoring rule;
- the covariance policy has not been promoted to the scoring benchmark;
- the branch responses are still preflight artifacts.

## Family Sign-Rule Preview

The row-level sign-rule preview is:

```text
python3 scripts/build_source_split_family_sign_rule_preview.py
```

It writes:

```text
evidence/source_split_family_sign_rule_preview.csv
evidence/source_split_family_sign_rule_preview_summary.csv
```

The preview rule is stable if all nonzero family signs agree. The current
preview gives three stable rows and five warning rows.
