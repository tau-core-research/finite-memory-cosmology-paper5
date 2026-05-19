# Public Covariance Policy Registry

Status: covariance and cross-covariance policy registry; no stronger rerun is
authorized.

The locked rerun protocol requires the covariance route to be declared before a
future public-covariance scorecard is interpreted. This registry separates
allowed, sensitivity-only, and forbidden covariance policies.

Outputs:

- `evidence/public_covariance_policy_registry.csv`;
- `evidence/public_covariance_policy_readiness.csv`.

## Registered Policies

The registry currently contains five policies:

1. `PCOV_POLICY_FULL_PUBLIC_LIKELIHOOD_NATIVE_V1`
   Preferred measurement route. It requires public SN+BAO likelihood covariance
   or an equivalent joint covariance release propagated into source-split space.
   It is not currently available.

2. `PCOV_POLICY_REGISTERED_SHRINKAGE_V1`
   Registered public benchmark proxy. It allows shrinkage only if lambda,
   correlation family, cross-covariance handling, and null policies are frozen
   before rerun. It is not currently available.

3. `PCOV_POLICY_ROW_ALIGNED_CROSS_COV_SENSITIVITY_V1`
   Sensitivity-only route. This is currently available, but it cannot select the
   best `rho_cross` as a benchmark and cannot support measurement validation.

4. `PCOV_POLICY_BRANCH_SCATTER_REGISTERED_V1`
   Secondary preflight bridge. It requires branch scatter to be classified in
   advance as a systematic floor or reconstruction-family scatter source. It is
   not currently available as a stronger policy.

5. `PCOV_POLICY_FORBIDDEN_TUNED_ROUTE`
   Forbidden route. Any covariance or cross-covariance selected after inspecting
   K2-vs-control scores is invalid for stronger interpretation.

## Current Readiness

The readiness output reports:

- currently available preflight policies: 1;
- currently available measurement policies: 0;
- primary available policy:
  `PCOV_POLICY_ROW_ALIGNED_CROSS_COV_SENSITIVITY_V1`;
- current status:
  `SENSITIVITY_POLICY_AVAILABLE_STRONGER_POLICY_BLOCKED`.

The next action is to freeze registered shrinkage parameters or implement a full
likelihood-native public covariance route before any stronger rerun is
interpreted.

The registered-shrinkage rerun template now records the structure of that
possible route. It is intentionally incomplete: shrinkage parameters and the
cross-covariance policy remain unregistered, so the route cannot yet be used for
a stronger scorecard.

The registered-shrinkage parameter policy now freezes a candidate future
preflight route. The policy is still not a measurement policy and does not allow
post-hoc selection among sensitivity-grid outcomes.
