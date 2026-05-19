# Physical Null Calibration Covariance Policy

Status: covariance policy registered; no physical-null source covariance is
available yet.

This policy defines how uncertainties for future backreaction-only and
Dyer-Roeder/optical calibration sources may enter the physical-null benchmark.

Outputs:

- `evidence/physical_null_calibration_covariance_policy.csv`;
- `evidence/physical_null_calibration_covariance_readiness.csv`.

## Preferred Route

The preferred measurement route is source-native covariance or uncertainty
propagated through the frozen physical-null mapping policy into the same
source-split rows.

If a source publishes row correlations, they must be used. If only diagonal
uncertainties are available, that must be declared explicitly and treated as a
weaker route.

## Preflight-Only Routes

Declared diagonal proxies and registered shrinkage/correlation proxies may be
used only for sensitivity checks. They cannot create measurement-validation
language.

## Forbidden Route

Uncertainty widening, shrinkage, or cross-row correlation selected after seeing
the K2 versus physical-null ranking is forbidden.

## Current Reading

```text
PhysicalNullCovarianceReady: false
PrimaryBlockingIssue: source_covariance_not_ingested_or_propagated
```

Thus the next step is source covariance ingestion and propagation, not K2
modification.

The aggregate physical-null status is tracked in
`docs/physical_null_readiness_dashboard.md`.
