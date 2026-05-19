# Registered Shrinkage Future-Preflight Scorecard

Status: future-preflight scorecard; no measurement validation claim.

This run consumes the registered-shrinkage parameter policy:

```text
lambda = 0.15
correlation_family = exp_minus_abs_delta_x_over_L
correlation_length = 0.25
rho_SN_BAO = 0.0
```

It does not change K2, does not refit K1, and does not select a best
cross-covariance route after seeing the scorecard.

Outputs:

- `evidence/registered_shrinkage_future_preflight_covariance.csv`;
- `evidence/registered_shrinkage_future_preflight_scorecard.csv`;
- `evidence/registered_shrinkage_future_preflight_summary.csv`.

## Result

The current summary reports:

```text
BestModel: POLY_DEG2
K1AIC: 16.61788646383459
K2AIC: 13.922797314092838
BestPolyAIC: 8.415746515836037
DeltaAIC_K2_minus_K1: -2.6950891497417526
DeltaAIC_K2_minus_BestPoly: 5.507050798256801
K2ImprovesOverK1: true
K2BeatsBestPoly: false
PositiveDefinite: true
AllowedRerunType: future_preflight_only
MeasurementValidationAllowed: false
```

## Interpretation

The registered-shrinkage route does not rescue K2 from the public-polynomial
objection. K2 still improves over K1/no-memory, but the quadratic polynomial
control remains stronger under this registered shrinkage covariance.

This is a useful weakening result. It shows that the shrinkage route was not
tuned into a K2 win. The next decisive work remains either a full public
likelihood-native covariance transform or a stronger independent justification
for a non-polynomial public benchmark route.

The polynomial-control fairness audit now records the policy consequence:
`POLY_DEG2` cannot be dismissed as unfair, but it also cannot be promoted to a
physical null explanation. It remains a mandatory overfit-risk blocker for
measurement validation.
