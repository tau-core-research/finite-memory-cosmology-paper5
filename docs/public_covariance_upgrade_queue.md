# Public Covariance Upgrade Queue

Status: next-step queue after the likelihood-native support ladder; no
measurement validation claim.

The support ladder shows that K2 is now supportive relative to K1/no-memory and
conditionally supportive against polynomial controls, but the public covariance
route remains the main blocker. This queue turns that blocker into concrete
tasks.

Outputs:

- `evidence/public_covariance_upgrade_queue.csv`;
- `evidence/public_covariance_upgrade_readiness.csv`.

## Current Readiness

The current readiness status is:

- K2-vs-K1 supportive: true;
- K2-vs-polynomial resolved: false;
- public covariance strong enough: false;
- public covariance proxy available: true;
- measurement validation route available: false;
- branch-scatter preflight allowed: true.

The current status is therefore
`PUBLIC_ROUTE_NOT_READY_FOR_MEASUREMENT_VALIDATION`.

## Blocking Tasks

The queue identifies three blocking items:

1. `PCOV_UPGRADE_1_FULL_TRANSFORM`
   Propagate public SN+BAO covariance through the registered likelihood-native
   source-split transform, or replace the current proxy with an explicitly
   declared shrinkage covariance.

2. `PCOV_UPGRADE_2_CROSS_COVARIANCE_POLICY`
   Register a SN-BAO cross-covariance construction before rerunning scorecards.
   It must not be tuned after seeing whether it helps K2.

3. `PCOV_UPGRADE_5_LOCKED_RERUN_PROTOCOL`
   Freeze covariance route, K1 source, nulls, coordinate mapping, and acceptance
   thresholds before any stronger public covariance rerun is interpreted.

## Partial And Preflight Items

The polynomial-control rule is partial: public leave-one-out still favors the
quadratic polynomial, while blocked validation and branch-scatter routes favor
K2. This must be reported in any public benchmark.

The branch-scatter route is allowed as declared preflight, but it must be
classified before stronger use: systematic floor, reconstruction-family
scatter, or sensitivity route.

## Next Action

The next useful work is to freeze a full public covariance route or a registered
shrinkage/scatter route. The locked K2 operator should remain unchanged.

The locked rerun protocol now exists as the guard for that next work. It
authorizes zero current stronger reruns, but it defines what a valid future
public-covariance rerun must declare before execution.

The covariance policy registry now defines which covariance routes can satisfy
that guard. The current answer is restrictive: only a sensitivity-level
row-aligned cross-covariance policy is available. Registered shrinkage and full
public covariance routes remain blocking tasks.

The registered-shrinkage rerun template turns the shrinkage blocker into two
specific missing pieces: the shrinkage parameter/correlation family and the
cross-covariance policy.

The registered-shrinkage parameter policy now fills those two pieces for a
future preflight route, while keeping current stronger reruns blocked.

The activation gate converts this into a clear status: registered shrinkage is
future-preflight activatable, but measurement validation remains blocked by
polynomial-control and public-measurement-route requirements.

The registered-shrinkage future-preflight result confirms that the
polynomial-control blocker remains real under the registered shrinkage policy.
