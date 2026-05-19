# Public Covariance Locked Rerun Protocol

Status: preregistration artifact; no current stronger rerun is authorized.

The public covariance upgrade queue identifies a key risk: because the current
result is route-dependent, the next stronger scorecard must not be selected
after seeing which route helps K2. This protocol freezes the allowed and
forbidden rerun paths before any such rerun is interpreted.

Outputs:

- `evidence/public_covariance_locked_rerun_protocol.csv`;
- `evidence/public_covariance_locked_rerun_readiness.csv`.

## Preferred Protocol

`PCOV_RERUN_FULL_LIKELIHOOD_NATIVE_V1` is the preferred public benchmark route.
It requires:

- frozen K2 operator from `frozen/k2_operator_v1.yaml`;
- `W(x)=1+rho*x^3`, `p=3`, `rho<=4`;
- frozen likelihood-native joint SN+BAO K1/no-memory baseline;
- public full or registered shrinkage SN+BAO covariance in source-split space;
- SN-BAO cross-covariance policy declared before the run;
- likelihood-native or declared coordinate-native mapping;
- null comparators reported under the same covariance and validation policy.

The preferred protocol is not ready because the full public covariance transform
or registered shrinkage route is missing.

## Secondary Protocol

`PCOV_RERUN_BRANCH_SCATTER_REGISTERED_V1` is a secondary preflight bridge. It
can only be used if branch scatter is registered before the rerun as a
systematic floor or reconstruction-family scatter route. It cannot be promoted
retroactively from a sensitivity result.

The secondary protocol is also not ready.

## Forbidden Protocol

`PCOV_RERUN_FORBIDDEN_RESCUE_ROUTE` captures invalid paths:

- K1 derived from current K2 residuals;
- covariance selected after seeing K2-vs-polynomial results;
- cross-covariance tuned to make K2 win;
- coordinate mapping changed after diagnosis as a rescue route;
- null comparators or validation modes dropped after inspection.

Any of these invalidates stronger interpretation.

## Current Readiness

The readiness output reports:

- allowed current rerun count: 0;
- measurement validation still blocked: true;
- primary blocker: full public covariance transform or registered shrinkage
  route missing.

The protocol is valuable because it locks the next valid comparison before the
next comparison is run.

The covariance policy registry now supplies the route catalogue for this
protocol. It currently marks only the row-aligned cross-covariance route as
available, and only as sensitivity. Therefore the allowed current stronger rerun
count remains zero.

The registered-shrinkage template is a candidate future route under this
protocol, but it is not ready. Its missing pieces are the shrinkage parameters
and the cross-covariance policy.

Those pieces are now frozen in the registered-shrinkage parameter policy for
future preflight use. The protocol still authorizes zero current stronger
reruns until the route is explicitly activated before execution.
