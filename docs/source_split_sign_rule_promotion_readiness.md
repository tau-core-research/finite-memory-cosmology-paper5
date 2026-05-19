# Source-Split Sign-Rule Promotion Readiness

Status: promotion readiness check added; promotion is blocked.

The family sign-rule preview is useful, but it is not the scoring rule. This
readiness check records the exact conditions required before the preview can be
promoted.

## Run

```text
python3 scripts/check_source_split_sign_rule_promotion.py
```

It writes:

```text
evidence/source_split_sign_rule_promotion_readiness.csv
```

## Current Decision

The rule is not promotable yet because the real reconstruction-family candidate
export is missing:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

The preview still remains useful because it records that warning rows must be
carried forward instead of being hidden as support or hidden as rejection.
