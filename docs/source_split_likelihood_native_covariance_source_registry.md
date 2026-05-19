# Source-Split Likelihood-Native Covariance Source Registry

Status: covariance source registry added.

The branch-scatter benchmark strengthened K2 under a declared preflight scale,
but the measurement-validation blocker is now specifically a covariance-source
blocker. This registry separates the available preflight route from the missing
independent routes.

```text
script: scripts/build_likelihood_native_covariance_source_registry.py
registry: evidence/source_split_likelihood_native_covariance_source_registry.csv
readiness: evidence/source_split_likelihood_native_covariance_source_readiness.csv
tasks: evidence/source_split_likelihood_native_covariance_source_task_queue.csv
```

## Current Readiness

```text
RawPublicCovariancesAvailable: True
PublicCovarianceProxyAvailable: True
PreflightBenchmarkRouteAvailable: True
MeasurementValidationRouteAvailable: False
BranchScatterPreflightAllowed: True
PrimaryBlockingIssue: full_likelihood_covariance_missing
```

The repo already contains raw public covariance inputs for DESI and Pantheon+,
and a first propagated covariance proxy now exists. The proxy is not a full
likelihood covariance because it uses the simplified source-split transform and
sets SN-BAO cross-covariance to zero. Therefore, the branch-scatter benchmark
remains the stronger preflight route, while the public proxy becomes the next
upgrade target.

## Registered Routes

- `PUBLIC_SN_BAO_FULL_PROPAGATED_COVARIANCE`: required independent route; raw
  public covariance files are available, but the transformed joint covariance is
  missing.
- `PUBLIC_SN_BAO_PROPAGATED_PROXY`: available public covariance proxy; not a
  full likelihood covariance.
- `PUBLIC_SYSTEMATIC_FLOOR`: required independent route; no external systematic
  floor is registered.
- `BRANCH_SCATTER_DECLARED_PREFLIGHT`: available preflight route; not public
  full covariance.
- `RECONSTRUCTION_FAMILY_SCATTER`: future candidate route; no frozen public
  reconstruction-family scatter rule exists yet.
- `NATIVE_DIAGONAL_PROXY`: available weakening baseline.

## Next Action

The next decisive task is to upgrade the public covariance proxy toward a full
likelihood covariance, including a clearer transform and any justified SN-BAO
cross-covariance treatment, or to register an independent systematic or
reconstruction-family scatter source.
