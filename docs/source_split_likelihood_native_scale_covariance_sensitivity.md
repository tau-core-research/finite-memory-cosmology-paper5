# Source-Split Likelihood-Native Scale/Covariance Sensitivity

Status: scale/covariance sensitivity complete.

The amplitude-gap diagnosis is now tested against several covariance and scale
proxies:

```text
evidence/source_split_likelihood_native_scale_covariance_sensitivity.csv
evidence/source_split_likelihood_native_scale_covariance_summary.csv
```

## Main Result

K2 improves over K1/no-memory in every tested covariance case, but usually does
not beat flexible polynomial controls.

```text
diag_native_sigma: K2 improves over K1, POLY_DEG2 dominates
diag_sigma_floor_0p10: K2 improves over K1, POLY_DEG3 dominates
diag_sigma_floor_0p25: K2 improves over K1, POLY_DEG3 dominates
diag_target_fraction_floor_10pct: K2 improves over K1, POLY_DEG3 dominates
diag_target_fraction_floor_25pct: K2 becomes best among tested models
nearest_neighbor_corr_0p25: K2 improves over K1, POLY_DEG2 dominates
constant_offdiag_corr_0p25: K2 improves over K1, POLY_DEG2 dominates
exp_corr_z: K2 improves over K1, POLY_DEG2 dominates
exp_corr_x: K2 improves over K1, POLY_DEG2 dominates
```

## Interpretation

This is a conditional result:

- The locked K2 response is consistently better than the likelihood-native K1
  baseline.
- Flexible controls remain stronger under most proxy covariance choices.
- K2 becomes competitive only when the low-depth amplitude residuals receive a
  target-fraction error floor at the 25 percent level.

That last case is not a measurement validation. It is a diagnostic clue that
the current conclusion depends strongly on the response-scale / error-model
definition. A public or independently declared covariance model is still
required before this branch can support a stronger empirical claim.

No post-hoc K1 rescaling and no `rho>4` rescue is authorized.

## Error-Floor Sweep

A finer target-fraction error-floor sweep has now been added:

```text
script: scripts/run_likelihood_native_error_floor_sweep.py
summary: evidence/source_split_likelihood_native_error_floor_sweep_summary.csv
```

The locked K2 response first becomes the best AIC model at a target-fraction
floor of `0.14`, and that is also the first floor where it beats the best
polynomial control. This is a diagnostic threshold only. It must be justified
independently by a public covariance model, systematic floor, or cross-branch
scatter before it can carry stronger empirical weight.

The follow-up policy check keeps the current status conservative: branch
scatter is large enough to be relevant, but remains a preflight control rather
than an eligible benchmark covariance.

The dedicated branch-scatter benchmark confirms that this route is important:
when the SN/BAO branch split is used as the row-level scale, `K2_LOCKED_RHO4`
is the best AIC model under all tested branch-scatter covariance variants.
This is stronger than the native diagonal proxy result, but it is still
preflight-level because the branch-scatter covariance is not public full
covariance.
