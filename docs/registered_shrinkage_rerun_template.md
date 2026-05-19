# Registered Shrinkage Rerun Template

Status: future-rerun template; not executable yet.

The public covariance policy registry shows that a registered shrinkage route
could become the next public-benchmark proxy, but only if its parameters are
declared before any new scorecard. This template freezes the structure of that
future rerun without running it.

Outputs:

- `evidence/registered_shrinkage_rerun_template.csv`;
- `evidence/registered_shrinkage_rerun_readiness.csv`.

## Template Components

The template has eight components:

- K2 operator;
- K1 source;
- covariance route;
- cross-covariance policy;
- coordinate mapping;
- null comparators;
- validation modes;
- acceptance rule.

Six of these are currently locked or available for preflight. Two remain
template-only:

- covariance route parameters;
- cross-covariance policy.

## Current Readiness

The readiness output reports:

- components: 8;
- locked/available components: 6;
- template-only components: 2;
- current allowed-to-run: false;
- measurement validation allowed: false.

The primary blocker is:

```text
shrinkage_parameters_and_cross_covariance_policy_not_registered
```

## Next Action

Before any registered-shrinkage rerun can be interpreted, the project must
choose and freeze:

- shrinkage lambda;
- correlation family;
- cross-covariance handling;
- whether the route is only preflight or can act as a declared public benchmark
  proxy.

The K2 kernel remains unchanged and `rho > 4` remains forbidden.

The companion parameter-policy artifact now freezes the primary future-preflight
choice:

```text
lambda = 0.15
correlation_family = exp_minus_abs_delta_x_over_L
correlation_length = 0.25
rho_SN_BAO = 0.0
```

This completes the template structurally, but does not authorize a current
rerun.

The activation gate confirms that the structurally complete route can be used
for future preflight only. It still cannot be interpreted as measurement
validation.

The future-preflight run under this template finds K2 better than K1/no-memory
but weaker than `POLY_DEG2`. The template therefore functions as an audit
discipline rather than a rescue route.
