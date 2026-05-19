# Source-Split Likelihood-Native K1 Promotion Gate

Status: promotion gate clean for preflight scoring; this is not measurement
validation.

The promotion gate is:

```text
python3 scripts/check_source_split_likelihood_native_k1_promotion.py
```

It writes:

```text
evidence/source_split_likelihood_native_k1_promotion_gate.csv
evidence/source_split_likelihood_native_k1_promotion_summary.csv
```

Current summary:

```text
Checks: 5
AvailableChecks: 5
PromotableChecks: 5
BlockingChecks: 0
PrimaryK1PromotionAllowed: True
```

## Current Checks

- `PROMO_BASELINE_VECTOR`: clean through the validated likelihood-native K1 export.
- `PROMO_COORDINATE_MAP`: clean through the CMB-chi coordinate policy and export.
- `PROMO_COVARIANCE_POLICY`: clean for declared preflight benchmark covariance.
- `PROMO_NULL_SCORECARD`: clean for preflight null scoring.
- `PROMO_EXTERNAL_K1_EXPORT`: clean as `likelihood_native_baseline`.

## Interpretation

This means the repo now has enough internally declared preflight objects to
score locked K2 against a likelihood-native K1 baseline and registered controls.
It does not mean that the finite-memory projection hypothesis is validated. The
first preflight scorecard shows K2 improving over K1, but simple polynomial
controls remain much stronger under the current diagonal proxy.
