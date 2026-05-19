# Likelihood-Native Polynomial Cross-Validation

Status: overfit-risk diagnostic only; no measurement validation claim.

The public covariance proxy scorecard is mixed because flexible polynomial
controls beat `K2_LOCKED_RHO4` under the in-sample AIC comparison. This audit
checks whether that polynomial advantage is stable under simple out-of-sample
tests on the likelihood-native source-split vector.

Outputs:

- `evidence/source_split_likelihood_native_polynomial_cv.csv`;
- `evidence/source_split_likelihood_native_polynomial_cv_summary.csv`.

## Method

The audit uses the same frozen K1 vector and locked K2 response:

- K1 is not refit;
- K2 uses `W(x)=1+rho*x^3`, `rho=4`, `p=3`;
- no `rho > 4` values are allowed;
- polynomial controls are refit only on training folds.

Three sigma routes are tested:

- `public_proxy_diag`;
- `branch_scatter_diag`;
- `native_plus_branch_scatter_quadrature`.

Two validation modes are reported:

- leave-one-out;
- blocked split over low/mid/high/sign-stable partitions where enough training
  points remain.

## Current Result

The cross-validation result is mixed but informative:

- under `public_proxy_diag`, `POLY_DEG2` still beats K2 in leave-one-out;
- under `public_proxy_diag`, K2 beats the polynomial controls in blocked split;
- under `branch_scatter_diag`, K2 beats the polynomial controls in both
  leave-one-out and blocked split;
- under `native_plus_branch_scatter_quadrature`, K2 also beats polynomial
  controls in both validation modes.

K2 improves over K1/no-memory in all reported comparison rows.

## Interpretation

The polynomial-control advantage is not uniformly stable. It remains present in
the public-proxy leave-one-out check, but it breaks under blocked validation and
under branch-scatter covariance routes. This strengthens the case that the
public-proxy in-sample polynomial dominance is an overfit-risk warning rather
than a final rejection of the finite-memory projection hypothesis.

The result is still preflight-level. A stronger claim requires a public
covariance-aware benchmark with a likelihood-native transform and registered
null comparators.
