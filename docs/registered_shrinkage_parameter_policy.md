# Registered Shrinkage Parameter Policy

Status: parameters frozen for a future preflight route; no current stronger
rerun is authorized.

The registered-shrinkage rerun template had two missing components:

- shrinkage covariance parameters;
- cross-covariance policy.

This artifact freezes a primary future-preflight policy for those missing
components without running a new scorecard.

Outputs:

- `evidence/registered_shrinkage_parameter_policy.csv`;
- `evidence/registered_shrinkage_parameter_policy_readiness.csv`.

## Primary Future-Preflight Policy

The primary registered policy is:

```text
PolicyID: REG_SHRINK_PARAM_BASELINE_V1
LambdaShrink: 0.15
CorrelationFamily: exp_minus_abs_delta_x_over_L
CorrelationLength: 0.25
RhoSNBAO: 0.0
CrossCovariancePolicy: zero_cross_covariance_primary_with_sensitivity_reported
```

The policy is sourced from the existing positive-definite shrinkage artifact:

```text
evidence/source_split_joint_covariance_policy_summary.csv
```

It was not selected by rerunning a new K2-vs-control scorecard.

## Sensitivity And Forbidden Routes

The registry also records:

- a sensitivity-only grid, which must be reported as a grid and cannot promote
  its best case to benchmark status;
- a forbidden tuned route, covering any parameter choice made after inspecting
  K2-vs-polynomial outcomes.

## Readiness

The readiness output reports:

- parameter policy registered: true;
- cross-covariance policy registered: true;
- template-only components before policy: 2;
- template-only components after policy: 0;
- can support future preflight rerun: true;
- current allowed-to-run: false;
- measurement validation allowed: false.

This means the registered-shrinkage route is now structurally complete for a
future preflight decision, but it is still not an authorized current rerun.

The activation gate now confirms the next boundary: future-preflight activation
is allowed, but current scorecard execution and measurement validation are not.

The future-preflight scorecard using this policy keeps the same boundary. It is
not a K2 win against polynomial controls; it is a useful registered-shrinkage
weakening result.
