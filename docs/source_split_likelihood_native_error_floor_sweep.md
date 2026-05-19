# Source-Split Likelihood-Native Error-Floor Sweep

Status: diagnostic sweep complete.

The likelihood-native source-split scorecard was rerun with a declared
target-fraction error floor applied to the diagonal proxy uncertainty:

```text
sigma_eff = max(sigma_native, f * abs(target_response))
```

The sweep uses `f` from `0.00` to `0.50` in steps of `0.01`.

```text
script: scripts/run_likelihood_native_error_floor_sweep.py
detail: evidence/source_split_likelihood_native_error_floor_sweep.csv
summary: evidence/source_split_likelihood_native_error_floor_sweep_summary.csv
```

## Main Result

The locked `K2_LOCKED_RHO4` response first becomes the best AIC model at a
target-fraction floor of `0.14`. The same threshold is also the first floor
where K2 beats the best polynomial control.

Selected checkpoints:

```text
f = 0.00: best = POLY_DEG2, K2 worse than best polynomial by DeltaAIC = 133812.91
f = 0.10: best = POLY_DEG3, K2 worse than best polynomial by DeltaAIC = 148.70
f = 0.13: best = POLY_DEG3, K2 worse than best polynomial by DeltaAIC = 12.00
f = 0.14: best = K2_LOCKED_RHO4, K2 better than best polynomial by DeltaAIC = -16.13
```

## Interpretation

This is not a measurement-validation result. It shows that K2 competitiveness
depends strongly on the independently declared response-scale / covariance
model. The `0.14` floor is a useful diagnostic threshold, not a value that may
be selected post hoc to rescue the locked operator.

The result narrows the next question:

- If a public covariance model, systematic floor, or cross-branch scatter
  independently motivates an error scale near or above this level, the
  likelihood-native K2 branch becomes more competitive.
- If the public covariance model remains close to the native diagonal proxy,
  flexible controls remain stronger and the branch stays in weakening status.
- No `rho>4`, kernel change, or K1 rescaling is authorized by this sweep.

The next task is therefore an error-floor justification policy, not a new
operator fit.

That policy gate is now tracked separately in
`docs/source_split_likelihood_native_error_floor_policy.md`.
