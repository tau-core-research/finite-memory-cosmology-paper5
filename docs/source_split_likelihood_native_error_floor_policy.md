# Source-Split Likelihood-Native Error-Floor Policy

Status: policy gate added; stronger K2 interpretation remains blocked.

The error-floor sweep found that the locked `K2_LOCKED_RHO4` response first
becomes AIC-competitive with the polynomial controls at a target-fraction floor
of `0.14`. This document records how that threshold can and cannot be used.

```text
script: scripts/build_likelihood_native_error_floor_policy.py
policy: evidence/source_split_likelihood_native_error_floor_policy.csv
summary: evidence/source_split_likelihood_native_error_floor_policy_summary.csv
```

## Current Policy Result

The current policy status is:

```text
error_floor_not_independently_justified
```

The branch has a useful preflight clue: the public SN/BAO branch-scatter
control has a median target-fraction scale above the `0.14` threshold. However,
that route is still marked as a preflight control rather than an eligible
benchmark covariance. It cannot be used as a stronger empirical argument until
it is upgraded into a declared covariance, systematic-floor, or
reconstruction-family scatter model.

## Allowed Uses

- Use `0.14` as a diagnostic threshold for future covariance and systematic
  checks.
- Report that K2 becomes competitive if an independently justified response
  scale reaches this level.
- Keep the native diagonal proxy as the weakening baseline.

## Forbidden Uses

- Do not select the `0.14` floor merely because it improves the K2 score.
- Do not treat branch scatter as public full covariance.
- Do not change the K2 kernel, use `rho>4`, or rescale K1 to match the target.

## Next Action

The next empirical task is to upgrade one of the independent routes:

- public full covariance propagated into the source-split diagnostic vector;
- independently published systematic floor;
- declared branch/reconstruction-family scatter model with a frozen rule.

Until then, the result is best read as conditional strengthening of K2, not as
measurement validation.

The first branch-scatter benchmark has now been run and supports this
conditional reading: K2 is best under the tested branch-scatter covariance
variants. The policy status remains unchanged because the route is still
preflight-level.
